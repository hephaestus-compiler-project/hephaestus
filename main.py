# pylint: disable=too-few-public-methods
from datetime import datetime
import json
import multiprocessing as mp
import os
import tempfile
import sys
import subprocess as sp
import shutil
import time
import traceback
from collections import namedtuple, OrderedDict

from src.args import args as cli_args
from src import utils
from src.compilers.kotlin import KotlinCompiler
from src.translators.kotlin import KotlinTranslator
from src.modules.processor import ProgramProcessor


TRANSLATORS = {
    'kotlin': KotlinTranslator
}
COMPILERS = {
    'kotlin': KotlinCompiler
}
STATS = {
    "Info": {
        "stop_cond": cli_args.stop_cond,
        "stop_cond_value": (
            cli_args.seconds
            if cli_args.stop_cond == "timeout"
            else cli_args.iterations
        ),
        "transformations": cli_args.transformations,
        "transformation_types": ",".join(cli_args.transformation_types),
        "bugs": cli_args.bugs,
        "name": cli_args.name,
        "language": cli_args.language
    },
    "totals": {
        "passed": 0,
        "failed": 0
    },
    "faults": {}
}
TEMPLATE_MSG = (u"Test Programs Passed {} / {} \u2714\t\t"
                "Test Programs Failed {} / {} \u2718\r")
ProgramRes = namedtuple("ProgramRes", ['failed', 'stats'])


# ============= util functions =======================

def print_msg():
    sys.stdout.write('\033[2K\033[1G')
    failed = STATS['totals']['failed']
    passed = STATS['totals']['passed']
    iterations = (
        cli_args.iterations
        if cli_args.iterations else passed + failed)
    msg = TEMPLATE_MSG.format(passed, iterations, failed, iterations)
    sys.stdout.write(msg)


def logging():
    compiler = COMPILERS[cli_args.language]
    _, compiler = run_command(compiler.get_compiler_version())
    compiler = compiler.strip()
    print("{} {} ({})".format("stop_cond".ljust(21), cli_args.stop_cond,
                              (cli_args.seconds
                               if cli_args.stop_cond == "timeout"
                               else cli_args.iterations)))
    print("{} {}".format("transformations".ljust(21),
                         cli_args.transformations))
    print("{} {}".format("transformation_types".ljust(21), ",".join(
          cli_args.transformation_types)))
    print("{} {}".format("bugs".ljust(21), cli_args.bugs))
    print("{} {}".format("name".ljust(21), cli_args.name))
    print("{} {}".format("language".ljust(21), cli_args.language))
    print("{} {}".format("compiler".ljust(21), compiler))
    utils.fprint("")

    if not cli_args.seconds and not cli_args.iterations:
        print()
        print(("Warning: To stop the tool press Ctr + c (Linux) or Ctrl + "
               "Break (Windows)"))
        print()

    print_msg()
    with open(cli_args.log_file, 'a') as out:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        out.write("{}; {}; {}; {}; {}\n".format(
            dt_string, cli_args.name, cli_args.bugs, cli_args.language,
            compiler))

    STATS['Info']['compiler'] = compiler


def run_command(arguments, get_stdout=True):
    """Run a command
    Args:
        A list with the arguments to execute. For example ['ls', 'foo']
    Returns:
        return status, stderr.
    """
    try:
        is_windows = os.name == 'nt'
        cmd = sp.Popen(arguments, stdout=sp.PIPE,
                       stderr=sp.STDOUT, shell=is_windows)
        stdout, stderr = cmd.communicate()
    except sp.CalledProcessError as err:
        return False, err
    stderr = stderr.decode("utf-8") if stderr else ""
    stdout = stdout.decode("utf-8") if stdout else ""
    err = stdout if get_stdout else stderr
    status = cmd.returncode == 0
    return status, err


def get_generator_dir(pid):
    return os.path.join(cli_args.test_directory, "generator",
                        "iter_" + str(pid))


def get_transformations_dir(pid, tid):
    return os.path.join(cli_args.test_directory, "transformations",
                        "iter_" + str(pid), str(tid))


def save_program(program, program_str, program_file):
    dst_dir = os.path.dirname(program_file)
    utils.mkdir(dst_dir)
    # Save the program
    utils.save_text(program_file, program_str)
    utils.dump_program(program_file + ".bin", program)


def save_stats():
    dst_dir = os.path.join(cli_args.test_directory)
    faults_file = os.path.join(dst_dir, 'faults.json')
    stats_file = os.path.join(dst_dir, "stats.json")
    utils.mkdir(dst_dir)
    faults = STATS.pop('faults')
    with open(faults_file, 'w') as out:
        json.dump(faults, out, indent=2)
    with open(stats_file, 'w') as out:
        json.dump(STATS, out, indent=2)


def stop_condition(iteration, time_passed):
    if cli_args.seconds:
        return time_passed < cli_args.seconds
    if cli_args.iterations:
        return iteration < cli_args.iterations + 1
    return True


def update_stats(res, batch):
    failed = len(res)
    passed = batch - failed
    STATS['totals']['failed'] += failed
    STATS['totals']['passed'] += passed
    STATS['faults'].update(res)
    if not cli_args.debug:
        print_msg()


def get_batches(programs):
    if cli_args.stop_cond == 'timeout':
        return cli_args.batch
    return min(cli_args.batch, cli_args.iterations - programs)


def gen_program(pid, dirname, package):
    """
    This function is responsible processing an iteration.

    It generates a program with a given id, it then applies a number of
    transformations, and finally it saves the resulting program into the
    given directory.

    The program belongs to the given package.
    """
    utils.random.reset_word_pool()
    translator = TRANSLATORS[cli_args.language](package)
    proc = ProgramProcessor(pid, translator, cli_args)
    program, oracle = proc.generate_program()
    if cli_args.keep_all:
        # Save the initial program.
        save_program(
            program,
            utils.translate_program(translator, program),
            os.path.join(get_generator_dir(pid), translator.get_filename())
        )
    program_str = None
    while proc.can_transform():
        try:
            program, oracle = proc.transform_program(program)
            if cli_args.keep_all:
                # Save every program resulted by the current transformation.
                program_str = utils.translate_program(translator, program)
                save_program(
                    program,
                    utils.translate_program(translator, program),
                    os.path.join(
                        get_transformations_dir(
                            pid, proc.current_transformation - 1),
                        translator.get_filename())
                )
        except Exception as exc:
            # This means that we have programming error in transformations
            err = ''
            if cli_args.print_stacktrace:
                err = str(traceback.format_exc())
            else:
                err = str(exc)
            if cli_args.debug:
                print(err)
            stats = {
                'transformations': [t.get_name()
                                    for t in proc.get_transformations()],
                'oracle': oracle,
                'error': err,
                'program': None
            }
            return ProgramRes(True, stats)
        except KeyboardInterrupt:
            return None

    if program_str is None:
        program_str = utils.translate_program(translator, program)
    dst_file = os.path.join(dirname, translator.get_filename())
    dst_file2 = os.path.join(cli_args.test_directory, str(pid),
                             translator.get_filename())
    save_program(program, program_str, dst_file)
    save_program(program, program_str, dst_file2)
    utils.dump_program(dst_file2 + ".bin", program)
    stats = {
        'transformations': [t.get_name()
                            for t in proc.get_transformations()],
        'oracle': oracle,
        'error': None,
        'program': dst_file
    }
    return ProgramRes(False, stats)


def gen_program_mul(pid, dirname, package):
    utils.random.r.seed()
    return gen_program(pid, dirname, package)


def _report_failed(pid, tid, compiler, oracle):
    """Find which program introduce the error and then report it.
    """
    translator = TRANSLATORS[cli_args.language]()
    prev_file = None
    while tid:
        program_file = os.path.join(get_transformations_dir(pid, tid),
                                    translator.get_filename())
        compiler = COMPILERS[cli_args.language](program_file)
        status, _ = run_command(compiler.get_compiler_cmd())
        if status == oracle:
            dst_file = os.path.join(cli_args.test_directory, str(pid),
                                    "initial_program.kt")
            dst_file2 = os.path.join(cli_args.test_directory, str(pid),
                                     "program.kt")
            shutil.copyfile(program_file, dst_file)
            shutil.copyfile(program_file + ".bin", dst_file + ".bin")
            if prev_file:
                shutil.copyfile(prev_file, dst_file2)
                shutil.copyfile(prev_file + ".bin", dst_file2 + ".bin")
            break

        prev_file = program_file
        tid -= 1


def check_oracle(dirname, oracles):
    """
    This function is responsible for checking the oracle of the generated
    programs.

    It gets a dict of oracles, and a directory that includes a batch of
    program.

    It first invokes the compiler to compile all the pograms included in the
    given directory. Then, based on the given oracles, it decides whether
    the compiler produced the expected output for every program.

    It returns a dictionary containing the programs where the compiler did not
    produce the expected results (and the reason why).
    """
    filename = os.path.join(dirname, 'src')
    compiler = COMPILERS[cli_args.language](filename)
    command_args = compiler.get_compiler_cmd()
    # At this point, we run the compiler
    _, err = run_command(command_args)
    # Analyze the compiler output and check whether there are programs
    # that the compiler did not manage to compile.
    failed = compiler.analyze_compiler_output(err)

    output = {}
    for pid, proc_res in oracles.items():
        if proc_res.failed:
            output[pid] = proc_res.stats
            continue
        program, oracle = (proc_res.stats['program'], proc_res.stats['oracle'])
        if oracle and program in failed:
            # Here the program should be compiled successfully. However,
            # it's in the list of the error messages.
            proc_res.stats['error'] = '\n'.join(failed[program])
            output[pid] = proc_res.stats
            if cli_args.debug:
                msg = 'Mismatch found in program {}. Expected to compile'
                print(msg.format(pid))
            if cli_args.rerun:
                _report_failed(pid, cli_args.transformations, compiler, oracle)
            continue
        if not oracle and program not in failed:
            # Here, we have a case where we expected that the compiler would
            # not be able to compile the program. However, the compiler
            # managed to compile it successfully.
            proc_res.stats['error'] = 'SHOULD NOT BE COMPILED'
            output[pid] = proc_res.stats
            if cli_args.debug:
                msg = 'Mismatch found in program {}. Expected to fail'
                print(msg.format(pid))
            if cli_args.rerun:
                _report_failed(pid, cli_args.transformations, compiler, oracle)
            continue
        shutil.rmtree(os.path.join(cli_args.test_directory, str(pid)))
    # Clear the directory of programs.
    shutil.rmtree(dirname)
    return output


def _run(process_program, process_res):
    logging()
    iteration = 1
    time_passed = 0
    start_time = time.time()
    try:
        while stop_condition(iteration, time_passed):
            tmpdir = tempfile.mkdtemp()
            res = []
            batches = get_batches(iteration - 1)
            for i in range(batches):
                package = utils.random.word()
                dirname = os.path.join(tmpdir, 'src', package)
                pid = iteration + i
                r = process_program(pid, dirname, 'src.' + package)
                res.append(r)

            process_res(iteration, res, tmpdir, batches)

            time_passed = time.time() - start_time
            iteration += batches
    except KeyboardInterrupt:
        pass


def run():

    def process_program(pid, dirname, package):
        return gen_program(pid, dirname, package)

    def process_res(start_index, res, testdir, batch):
        oracles = OrderedDict()
        for i, r in enumerate(res):
            oracles[start_index + i] = r
        res = {} if cli_args.dry_run else check_oracle(testdir, oracles)
        update_stats(res, batch)

    try:
        _run(process_program, process_res)
    except KeyboardInterrupt:
        pass
    save_stats()
    print()
    print("Total faults: " + str(STATS['totals']['failed']))


def run_parallel():

    pool = mp.Pool(cli_args.workers)

    def process_program(pid, dirname, package):
        return pool.apply_async(gen_program_mul, args=(pid, dirname, package))

    def process_res(start_index, res, testdir, batch):
        def update(res):
            update_stats(res, batch)

        res = [r.get() for r in res]
        oracles = OrderedDict()
        for i, r in enumerate(res):
            oracles[start_index + i] = r
        if cli_args.dry_run:
            return update({})
        pool.apply_async(check_oracle, args=(testdir, oracles),
                         callback=update)

    _run(process_program, process_res)
    try:
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
    save_stats()
    print()
    print("Total faults: " + str(STATS['totals']['failed']))


def main():
    if cli_args.debug or cli_args.workers is None:
        run()
    else:
        run_parallel()


if __name__ == "__main__":
    main()
