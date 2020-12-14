import os
import time
import tempfile
import pickle
import traceback
import subprocess as sp
from copy import deepcopy
from collections import defaultdict
from src.generators.Generator import Generator
from src.transformations.substitution import (
    ValueSubstitution, TypeSubstitution)
from src.transformations.type_creation import (
    SupertypeCreation, SubtypeCreation)
from src.transformations.parameterized import ParameterizedSubstitution
from src.translators.kotlin import KotlinTranslator
from src.utils import mkdir, random, fprint


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

    def __init__(self, args):
        self.args = args
        self.mismatch = 1  # mismatch counter
        self.transformations = [
            Executor.TRANSFORMATIONS[t]
            for t in self.args.transformation_types
        ]
        self.iterations = defaultdict(lambda: [list(), False])

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

    def _report(self, program_str, program, initial_p=None):
        mismatch = os.path.join(self.args.test_directory, str(self.mismatch))
        self.mismatch += 1
        mkdir(mismatch)
        # Save the program
        dst_filename = os.path.join(mismatch, self.translator.get_filename())
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
        print("Mismatch found: {}".format(mismatch))

    def _translate_program(self, p):
        self.translator = KotlinTranslator()
        self.translator.visit(p)
        return self.translator.result()

    def _generate_program(self):
        generator = Generator(max_depth=self.args.max_depth)
        p = generator.generate()
        program_str = self._translate_program(p)
        if self.args.keep_all:
            dst_dir = os.path.join(self.args.test_directory, "generator")
            mkdir(dst_dir)
            # Save the program
            dst_filename = os.path.join(dst_dir, self.translator.get_filename())
            with open(dst_filename, 'w') as out:
                out.write(program_str)
        status, _ = self._compile(program_str, compiler_pass=True)
        if not status:
            self._report(program_str, p)
            return False
        return True, p

    def _apply_trasnformation(self, transformation_number, program, comp, i):
        transformer = random.choice(self.transformations)()
        self.iterations[i][0].append(transformer.get_name())
        print('Applying tranformation {}: {}'.format(
            str(transformation_number + 1), transformer.get_name()
        ))
        prev_p = deepcopy(program)
        transformer.visit(program)
        p = transformer.result()
        if p is None:
            return "continue", prev_p
        program_str = self._translate_program(p)
        if self.args.keep_all:
            dst_dir = os.path.join(self.args.test_directory,
                                   "transformations",
                                   str(transformation_number))
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
            self._report(program_str, p, prev_p)
            self.iterations[i][1] = True
            return "break", p
        return "succeed", p

    def _apply_trasnformations(self, program, i):
        try:
            for j in range(self.args.transformations):
                comp = True
                if self.args.only_last and j != self.args.transformations - 1:
                    comp = False
                status, program = self._apply_trasnformation(j, program, comp, i)
                if status == "continue":
                    continue
                if status == "break":
                    break
        except Exception as e:
            # This means that we have programming error in transformations
            if self.args.print_stacktrace:
                print(traceback.format_exc())
            print(e)

    def run(self):
        for i in range(self.args.iterations):
            print()
            if self.args.replay:
                fprint('Processing program ' + self.args.replay)
                with open(self.args.replay, 'rb') as initial_bin:
                    program = pickle.load(initial_bin)
                program_str = self._translate_program(program)
                status, _ = self._compile(program_str, compiler_pass=True)
                if not status:
                    self._report(program_str, program)
                    break
            else:
                fprint('Processing program ' + str(i + 1))
                succeed, program = self._generate_program()
                if not succeed:
                    continue
            self._apply_trasnformations(program, i)

            random.reset_word_pool()
        print("\nTotal mismatches: {}".format(str(self.mismatch - 1)))
        for k, v in self.iterations.items():
            if v[1]:
                print("Iteration {}: {}".format(k, ", ".join(v[0])))
