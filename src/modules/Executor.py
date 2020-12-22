import os
import time
import tempfile
import pickle
import traceback
import subprocess as sp
import sys
from copy import deepcopy
from collections import defaultdict

from src.generators.Generator import Generator
from src.transformations.substitution import (
    ValueSubstitution, TypeSubstitution)
from src.transformations.type_creation import (
    SupertypeCreation, SubtypeCreation)
from src.transformations.parameterized import ParameterizedSubstitution
from src.translators.kotlin import KotlinTranslator
from src.utils import mkdir, random


def get_key(key):
    return "Iteration_{}".format(str(key))


def run_command(arguments):
    """Run a command
    Args:
        A list with the arguments to execute. For example ['ls', 'foo']
    Returns:
        return status, stderr.
    """
    try:
        cmd = sp.Popen(arguments, stdout=sp.PIPE, stderr=sp.STDOUT)
        _, stderr = cmd.communicate()
    except Exception as e:
        return False, e
    stderr = stderr.decode("utf-8") if stderr else ""
    status = True if cmd.returncode == 0 else False
    return status, stderr


class Executor:

    TRANSFORMATIONS = {
        'SupertypeCreation': SupertypeCreation,
        'SubtypeCreation': SubtypeCreation,
        'ValueSubstitution': ValueSubstitution,
        'TypeSubstitution': TypeSubstitution,
        'ParameterizedSubstitution': ParameterizedSubstitution
    }

    def __init__(self, exec_id, args):
        self.exec_id = exec_id
        self.args = args
        self.mismatch = 1  # mismatch counter
        self.transformations = [
            Executor.TRANSFORMATIONS[t]
            for t in self.args.transformation_types
        ]
        self.stats = defaultdict(lambda: {
            "transformations": list(),
            "error": "",
            "failed": False})
        self.tstack = []  # Transformation programs stack

    def _compile(self, program_str, compiler_pass=False):
        """Try to compile the generated program.

        Args:
            program_str: str
                Source code of the generated program.
            compiler_pass: bool
                If False the compiler must return an error

        Returns:
            bool: It depends on the compiler_pass argument. For instance, if
                compiler_pass is False, then it returns True if the compiler
                returns an error.

        """
        with tempfile.TemporaryDirectory() as tmpdirname:
            filename = os.path.join(tmpdirname, self.translator.get_filename())
            executable = os.path.join(tmpdirname, self.translator.get_executable())
            command_args = self.translator.get_cmd_build(filename, executable)
            with open(filename, 'w') as out:
                out.write(program_str)
            status, err = run_command(command_args)
            return not(bool(compiler_pass) ^ bool(status)), err

    def _report_failed(self):
        """Find which program introduce the error and then report it.
        """
        prev_str = ""
        prev_p = None
        while True:
            program, transformer = self.tstack.pop()
            if program is None:
                continue
            program_str = self._translate_program(program)
            if program == prev_p:
                continue
            preserve_correctness = True if isinstance(
                transformer, str) else transformer.preserve_correctness()
            status, _ = self._compile(
                self.translator.result(),
                compiler_pass=preserve_correctness
            )
            if status:
                self._report(prev_str, prev_p, program)
                # Update stats
                key = get_key(self.exec_id)
                transformations = self.stats[key]['transformations'][:len(
                    self.tstack) + 1]
                self.stats[key]['transformations'] = transformations
                break
            prev_p = deepcopy(program)
            prev_str = program_str

    def _report(self, program_str, program, initial_p=None):
        mismatch = os.path.join(self.args.test_directory, str(self.exec_id))
        self.mismatch += 1
        mkdir(mismatch)
        # Save the program
        dst_filename = os.path.join(mismatch, self.translator.get_filename())
        if self.args.debug:
            print("Program: " + dst_filename)
        with open(dst_filename, 'w') as out:
            out.write(program_str)
        with open(dst_filename + ".bin", 'wb') as out:
            pickle.dump(program, out)
        # Save initial (previous) program
        if initial_p:
            initial_filename = os.path.join(mismatch, "initial")
            with open(initial_filename + "_" + self.translator.get_filename(), 'w') as out:
                out.write(self._translate_program(initial_p))
            with open(initial_filename + ".bin", 'wb') as out:
                pickle.dump(initial_p, out)
        # Create a test script
        dst_executable = os.path.join(mismatch, self.translator.get_executable())
        cmd_build = self.translator.get_cmd_build(dst_filename, dst_executable)
        cmd_exec = self.translator.get_cmd_exec(dst_executable)
        testfile = os.path.join(mismatch, 'test.sh')
        with open(testfile, 'w') as out:
            out.write(' '.join(cmd_build) + '\n')
            out.write(' '.join(cmd_exec))

    def _translate_program(self, p):
        self.translator = KotlinTranslator()
        self.translator.visit(p)
        return self.translator.result()

    def _generate_program(self, i):
        # TODO return program_str
        if self.args.debug:
            print("\nIteration: " + str(i))
        generator = Generator(max_depth=self.args.max_depth)
        p = generator.generate()
        program_str = self._translate_program(p)
        if self.args.keep_all:
            dst_dir = os.path.join(self.args.test_directory, "generator",
                                   "iter_" + str(i))
            mkdir(dst_dir)
            # Save the program
            dst_filename = os.path.join(dst_dir, self.translator.get_filename())
            with open(dst_filename, 'w') as out:
                out.write(program_str)
        status, _ = self._compile(program_str, compiler_pass=True)
        if not status:
            self._report(program_str, p)
            return False, p, program_str
        return True, p, program_str

    def _apply_trasnformation(self, transformation_number, program, comp, i):
        transformer = random.choice(self.transformations)()
        if self.args.debug:
            print("Transformation: " + transformer.get_name())
        self.stats[get_key(i)]['transformations'].append(transformer.get_name())
        prev_p = deepcopy(program)
        transformer.visit(program)
        p = transformer.result()
        self.tstack.append((deepcopy(p), transformer))
        if p is None:
            return "continue", prev_p
        program_str = self._translate_program(p)
        if self.args.keep_all:
            dst_dir = os.path.join(self.args.test_directory,
                                   "transformations",
                                   "iter_" + str(i),
                                   str(transformation_number + 1))
            mkdir(dst_dir)
            # Save the program
            dst_filename = os.path.join(dst_dir, self.translator.get_filename())
            with open(dst_filename, 'w') as out:
                out.write(program_str)
        if not comp:
            return "succeed", p
        status, _ = self._compile(
            self.translator.result(),
            compiler_pass=transformer.preserve_correctness()
        )
        if not status:
            if self.args.debug:
                print("Mismatch found: {}(iter) {}(trans)".format(
                    str(i), str(transformation_number)
                ))
            if self.args.rerun:
                self._report_failed()
            else:
                self._report(program_str, p, prev_p)
            return "break", p
        return "succeed", p

    def _apply_trasnformations(self, program, i):
        failed = False
        try:
            for j in range(self.args.transformations):
                comp = True
                if ((self.args.only_last or self.args.rerun) and
                    j != self.args.transformations - 1):
                    comp = False
                status, program = self._apply_trasnformation(j, program, comp, i)
                if status == "continue":
                    continue
                if status == "break":
                    failed = True
                    break
        except Exception as e:
            # This means that we have programming error in transformations
            err = ''
            if self.args.print_stacktrace:
                err = str(traceback.format_exc())
            else:
                err = str(e)
            if self.args.debug:
                print(err)
            failed = True
            self.stats[get_key(i)]['error'] = err
        if failed:
            self.stats[get_key(i)]['failed'] = True
        return failed

    def process_program(self):
        if self.args.replay:
            print("\nIteration: " + str(self.exec_id))
            with open(self.args.replay, 'rb') as initial_bin:
                program = pickle.load(initial_bin)
            program_str = self._translate_program(program)
            status, _ = self._compile(program_str, compiler_pass=True)
            if not status:
                self._report(program_str, program)
                return True, dict(self.stats)
        else:
            succeed, program, program_str = self._generate_program(self.exec_id)
            if not succeed:
                self._report(program_str, program)
                return True, dict(self.stats)
        self.tstack.append((deepcopy(program), "InputProgram"))
        return self._apply_trasnformations(program, self.exec_id), dict(self.stats)
