#! /usr/bin/python3
# pylint: disable=global-statement
import multiprocessing as mp
import sys
import os
import json
from collections import namedtuple

from src.args import args
from src.utils import random, mkdir
from src.modules.executor import Executor


N_FAILED = 0
N_PASSED = 0
STATS = {}
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


if args.debug:
    for i in range(1, args.iterations + 1):
        res = run(i)
        STATS.update(res.stats)
        if res.failed:
            N_FAILED += 1
        else:
            N_PASSED += 1
    print("Total faults: " + str(N_FAILED))
    save_stats()
    sys.exit()


TEMPLATE_MSG = (u"Test Programs Passed {} / {} \u2714\t\t"
                "Test Programs Failed {} / {} \u2718\r")


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
    msg = TEMPLATE_MSG.format(N_PASSED, args.iterations, N_FAILED,
                              args.iterations)
    sys.stdout.write(msg)


def error_callback(exception):
    print(exception)


pool = mp.Pool(args.workers)
sys.stdout.write(TEMPLATE_MSG.format(
    N_PASSED, args.iterations, N_FAILED, args.iterations))
for i in range(1, args.iterations + 1):
    pool.apply_async(
        run, args=(i,), callback=process_result, error_callback=error_callback)
pool.close()
pool.join()
save_stats()
print()
