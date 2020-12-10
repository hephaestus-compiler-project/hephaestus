import os
import time
import tempfile
import pickle
import subprocess as sp
from copy import deepcopy
from src.generators.Generator import Generator
from src.transformations.substitution import (
    ValueSubstitution, TypeSubstitution)
from src.transformations.type_creation import (
    SupertypeCreation, SubtypeCreation)
from src.transformations.parameterized import ParameterizedSubstitution
from src.translators.kotlin import KotlinTranslator
from src.utils import mkdir, random


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

    def _report(self, program_str, initial_p=None):
        mismatch = os.path.join(self.args.test_directory, str(self.mismatch))
        self.mismatch += 1
        mkdir(mismatch)
        # Save the program
        dst_filename = os.path.join(mismatch, self.translator.get_filename())
        with open(dst_filename, 'w') as out:
            out.write(program_str)
        # Save initial (previous) program
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
        generator = Generator()
        p = generator.generate()
        program_str = self._translate_program(p)
        status, _ = self._compile(program_str, compiler_pass=True)
        if not status:
            self._report(program_str)
            return False
        return True, p

    def _apply_trasnformation(self, transformation_number, program):
        transformer = random.choice(self.transformations)()
        print('Applying tranformation {}: {}'.format(
            str(transformation_number + 1), transformer.get_name()
        ))
        prev_p = deepcopy(program)
        transformer.visit(program)
        p = transformer.result()
        if p is None:
            return "continue", prev_p
        program_str = self._translate_program(p)
        status, _ = self._compile(
            self.translator.result(),
            compiler_pass=transformer.preserve_correctness()
        )
        if not status:
            self._report(program_str, prev_p)
            return "break", p
        return "succeed", p

    def _apply_trasnformations(self, program):
        try:
            for j in range(self.args.transformations):
                status, program = self._apply_trasnformation(j, program)
                if status == "continue":
                    continue
                if status == "break":
                    break
        except Exception as e:
            # This means that we have programming error in transformations
            print(e)

    def run(self):
        # Set counter to time_end in case of timeout option
        #  counter = 1 if self.args.stop_cond == "number" else time.time() + self.args.seconds
        #  while True:
        for i in range(self.args.iterations):
            if self.args.replay:
                print('\nProcessing program ' + self.args.replay)
                with open(self.args.replay, 'rb') as initial_bin:
                    program = pickle.load(initial_bin)
            else:
                print('\nProcessing program ' + str(i + 1))
                succeed, program = self._generate_program()
                if not succeed:
                    continue
            self._apply_trasnformations(program)

            random.reset_word_pool()
        print("\nTotal mismatches: {}".format(str(self.mismatch - 1)))
            #  break
            #if self.args.stop_cond == "number":
            #    counter += 1
            #    print(counter)
            #    if counter > self.args.iterations:
            #        break
            #elif time.time() > counter:
            #    break
            #    temp_p = p
            #    for _ in range(self.args.transformations):
            #        p1 = self.transformer.transform(temp_p)
            #        temp_p = p1
            #    p2 = self.transformer.inject_fault(p1)
            #    program_str = self.translator.dummy_concretize_random(p2)
            #    status, _, filename = self._compile(program_str)
            #    if not status:
            #        self._report(filename)
            # Check stop_cond
