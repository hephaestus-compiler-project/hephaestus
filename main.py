#! /usr/bin/python3
import multiprocessing as mp
import sys

from src.args import args
from src.utils import random
from src.modules.Executor import Executor


def run(i):
    random.r.seed()
    executor = Executor(i, args)
    return executor.process_program()


n_failed = 0
n_passed = 0
template_msg = (u"Test Programs Passed {} / {} \u2714\t\t"
                "Test Programs Failed {} / {} \u2718\r")
def process_result(failed):
    global n_failed
    global n_passed
    if failed:
        n_failed += 1
    else:
        n_passed += 1
    sys.stdout.write('\033[2K\033[1G')
    msg = template_msg.format(n_passed, args.iterations, n_failed,
                              args.iterations)
    sys.stdout.write(msg)

pool = mp.Pool(args.workers)
sys.stdout.write(template_msg.format(
    n_passed, args.iterations, n_failed, args.iterations))
for i in range(1, args.iterations + 1):
    pool.apply_async(run, args=(i,), callback=process_result)
pool.close()
pool.join()
