#! /usr/bin/python3
# pylint: disable=global-statement
import multiprocessing as mp
import sys
import os
import json
import time
from collections import namedtuple
from datetime import datetime

from src.args import args
from src.utils import random, mkdir, fprint
from src.modules.executor import Executor, run_command


STOP_FLAG = False
N_FAILED = 0
N_PASSED = 0
STATS = {
    "Info": {
        "stop_cond": args.stop_cond,
        "stop_cond_value": args.seconds if args.stop_cond == "timeout" \
            else args.iterations,
        "transformations": args.transformations,
        "transformation_types": ",".join(args.transformation_types),
        "bugs": args.bugs,
        "name": args.name,
        "language": args.language
    },
    "Totals": {
        "PASSED": 0,
        "FAILED": 0
    }
}
FAULTS = {}
TEMPLATE_MSG = (u"Test Programs Passed {} / {} \u2714\t\t"
                "Test Programs Failed {} / {} \u2718\r")
ProcessRes = namedtuple("ProcessRes", ['failed', 'stats'])


def logging():
    global STATS
    translator = Executor.TRANSLATORS[args.language]()
    _, compiler = run_command(translator.get_cmd_compiler_version())
    compiler = compiler.strip()
    print("{} {} ({})".format("stop_cond".ljust(21), args.stop_cond,
                              args.seconds if args.stop_cond == "timeout"
                              else args.iterations))
    print("{} {}".format("transformations".ljust(21), args.transformations))
    print("{} {}".format("transformation_types".ljust(21), ",".join(
          args.transformation_types)))
    print("{} {}".format("bugs".ljust(21), args.bugs))
    print("{} {}".format("name".ljust(21), args.name))
    print("{} {}".format("language".ljust(21), args.language))
    print("{} {}".format("compiler".ljust(21), compiler))
    fprint("")

    if not args.seconds and not args.iterations:
        print()
        print(("Warning: To stop the tool press Ctr + c (Linux) or Ctrl + "
               "Break (Windows)"))
        print()

    with open(args.log_file, 'a') as out:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        out.write("{}; {}; {}; {}; {}\n".format(
            dt_string, args.name, args.bugs, args.language, compiler))

    STATS['Info']['compiler'] = compiler


def save_stats():
    global STATS
    global FAULTS
    dst_dir = os.path.join(args.test_directory)
    stats_file = os.path.join(dst_dir, 'stats.json')
    faults_file = os.path.join(dst_dir, 'faults.json')
    mkdir(dst_dir)
    with open(stats_file, 'w') as out:
        json.dump(STATS, out, indent=2)
    with open(faults_file, 'w') as out:
        json.dump(FAULTS, out, indent=2)


def run(iteration_number):
    try:
        random.r.seed()
        random.reset_word_pool()
        executor = Executor(iteration_number, args)
        failed, status = executor.process_program()
        return ProcessRes(failed=failed, stats=status)
    except KeyboardInterrupt:
        global STOP_FLAG
        STOP_FLAG = True
        return None


def stop_condition(iteration, time_passed):
    if args.seconds:
        return time_passed < args.seconds
    if args.iterations:
        return iteration < args.iterations + 1
    return True


def debug(time_passed, start_time):
    global STOP_FLAG
    global N_FAILED
    global N_PASSED
    global STATS
    iteration = 1
    while stop_condition(iteration, time_passed):
        res = run(iteration)
        if res is not None:
            if res:
                STATS.update(res.stats)
            if res.failed:
                N_FAILED += 1
                STATS['Totals']['FAILED'] = N_FAILED
                FAULTS.update(res.stats)
            else:
                N_PASSED += 1
                STATS['Totals']['PASSED'] = N_PASSED
        time_passed = time.time() - start_time
        iteration += 1
        save_stats()
        if STOP_FLAG:
            break
    save_stats()
    print()
    print("Total faults: " + str(N_FAILED))
    sys.exit()


def print_msg():
    global N_FAILED
    global N_PASSED
    sys.stdout.write('\033[2K\033[1G')
    iterations = args.iterations if args.iterations else N_PASSED + N_FAILED
    msg = TEMPLATE_MSG.format(N_PASSED, iterations, N_FAILED, iterations)
    sys.stdout.write(msg)


def process_result(result):
    try:
        global N_FAILED
        global N_PASSED
        global STATS
        if result:
            STATS.update(result.stats)
            if result.failed:
                N_FAILED += 1
                STATS['Totals']['FAILED'] = N_FAILED
                FAULTS.update(result.stats)
            else:
                N_PASSED += 1
                STATS['Totals']['PASSED'] = N_PASSED
            print_msg()
            save_stats()
    except KeyboardInterrupt:
        pass


def error_callback(exception):
    print(exception)


def multi_processing(time_passed, start_time):
    global N_FAILED
    global N_PASSED
    print_msg()
    if args.iterations:
        pool = mp.Pool(args.workers)
        for i in range(1, args.iterations + 1):
            pool.apply_async(
                run,
                args=(i,),
                callback=process_result,
                error_callback=error_callback)
        try:
            pool.close()
            pool.join()
        except KeyboardInterrupt:
            pool.terminate()
            pool.join()
            stop_flag = True
            print_msg()
            save_stats()
    # If we want to stop after X seconds we must run them in batches
    else:
        iteration = 0
        stop_flag = False
        while stop_condition(iteration, time_passed):
            pool = mp.Pool(args.workers)
            for i in range(0, args.workers):
                iteration += 1
                pool.apply_async(
                    run,
                    args=(iteration,),
                    callback=process_result,
                    error_callback=error_callback)
            try:
                pool.close()
                pool.join()
            except KeyboardInterrupt:
                pool.terminate()
                pool.join()
                stop_flag = True
                print_msg()
                save_stats()
            time_passed = time.time() - start_time
            if stop_flag:
                break
    print()


def main():
    logging()
    time_passed = 0
    start_time = time.time()
    if args.debug:
        debug(time_passed, start_time)
    multi_processing(time_passed, start_time)


if __name__ == "__main__":
    main()
