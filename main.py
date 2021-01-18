#! /usr/bin/python3
# pylint: disable=global-statement
import multiprocessing as mp
import sys
import os
import json
import time
from collections import namedtuple

from src.args import args
from src.utils import random, mkdir
from src.modules.executor import Executor


N_FAILED = 0
N_PASSED = 0
STATS = {}
TEMPLATE_MSG = (u"Test Programs Passed {} / {} \u2714\t\t"
                "Test Programs Failed {} / {} \u2718\r")
ProcessRes = namedtuple("ProcessRes", ['failed', 'stats'])


def save_stats():
    global STATS
    dst_dir = os.path.join(args.test_directory)
    dst_file = dst_dir + '/stats.json'
    mkdir(dst_dir)
    with open(dst_file, 'w') as out:
        json.dump(STATS, out, indent=2)


def run(iteration_number):
    random.r.seed()
    random.reset_word_pool()
    executor = Executor(iteration_number, args)
    failed, status = executor.process_program()
    return ProcessRes(failed=failed, stats=status)


def stop_condition(iteration, time_passed):
    if args.seconds:
        return time_passed < args.seconds
    return iteration < args.iterations + 1


def debug(time_passed, start_time):
    global N_FAILED
    global N_PASSED
    global STATS
    iteration = 1
    while stop_condition(iteration, time_passed):
        res = run(iteration)
        STATS.update(res.stats)
        if res.failed:
            N_FAILED += 1
        else:
            N_PASSED += 1
        time_passed = time.time() - start_time
        iteration += 1
        save_stats()
    print("Total faults: " + str(N_FAILED))
    sys.exit()


def process_result(result):
    global N_FAILED
    global N_PASSED
    global STATS
    STATS.update(result.stats)
    if result.failed:
        N_FAILED += 1
    else:
        N_PASSED += 1
    sys.stdout.write('\033[2K\033[1G')
    iterations = args.iterations if args.iterations else N_PASSED + N_FAILED
    msg = TEMPLATE_MSG.format(N_PASSED, iterations, N_FAILED, iterations)
    sys.stdout.write(msg)
    save_stats()


def error_callback(exception):
    print(exception)


def multi_processing(time_passed, start_time):
    global N_FAILED
    global N_PASSED
    sys.stdout.write(TEMPLATE_MSG.format(
        N_PASSED, args.iterations, N_FAILED, args.iterations))
    # If we want to stop after X seconds we must run them in batches
    if args.seconds:
        iteration = 0
        while stop_condition(iteration, time_passed):
            pool = mp.Pool(args.workers)
            for i in range(0, args.workers):
                iteration += 1
                pool.apply_async(
                    run,
                    args=(iteration,),
                    callback=process_result,
                    error_callback=error_callback)
            pool.close()
            pool.join()
            time_passed = time.time() - start_time
    else:
        pool = mp.Pool(args.workers)
        for i in range(1, args.iterations + 1):
            pool.apply_async(
                run,
                args=(i,),
                callback=process_result,
                error_callback=error_callback)
        pool.close()
        pool.join()
    print()


def main():
    time_passed = 0
    start_time = time.time()
    if args.debug:
        debug(time_passed, start_time)
    multi_processing(time_passed, start_time)


if __name__ == "__main__":
    main()
