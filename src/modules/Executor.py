import os
import time
import subprocess as sp
from shutil import copyfile
from src.generators.Generator import Generator
from src.transformations.Transformer import Transformer
from src.translators.kotlin import KotlinTranslator
from src.utils import mkdir


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

    def __init__(self, args):
        self.args = args
        self.transformer = Transformer()

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
        filename = os.path.join(self.args.temp_directory,
                                self.translator.get_filename())
        executable = os.path.join(
            self.args.temp_directory, self.translator.get_executable())
        command_args = self.translator.get_cmd_build(filename, executable)
        if not os.path.isdir(self.args.temp_directory):
            mkdir(self.args.temp_directory)
        with open(filename, 'w') as out:
            out.write(program_str)
        status, err = run_command(command_args)
        return not(bool(compiler_pass) ^ bool(status)), err, filename

    def _report(self, filename):
        mismatches = list(map(int, os.listdir(self.args.test_directory)))
        mismatch_number = "1" if not mismatches else str(max(mismatches) + 1)
        mismatch = os.path.join(self.args.test_directory, mismatch_number)
        mkdir(mismatch)
        dst_filename = os.path.join(mismatch, self.translator.get_filename())
        dst_executable = os.path.join(mismatch, self.translator.get_executable())
        copyfile(filename, dst_filename)
        cmd_build = self.translator.get_cmd_build(dst_filename, dst_executable)
        cmd_exec = self.translator.get_cmd_exec(dst_executable)
        testfile = os.path.join(mismatch, 'test.sh')
        with open(testfile, 'w') as out:
            out.write(' '.join(cmd_build) + '\n')
            out.write(' '.join(cmd_exec))
        print("Mismatch found: {}".format(mismatch))

    def run(self):
        # Set counter to time_end in case of timeout option
        counter = 1 if self.args.stop_cond == "number" else time.time() + self.args.seconds
        while True:
            self.generator = Generator()
            p = self.generator.generate()
            self.translator = KotlinTranslator()

            self.translator.visit(p)
            status, _, filename = self._compile(self.translator.get_program(),
                                                compiler_pass=True)
            if not status:
                self._report(filename)
            #for _ in range(self.args.rounds):
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
            if self.args.stop_cond == "number":
                counter += 1
                if counter > self.args.iterations:
                    break
            elif time.time() > counter:
                break
