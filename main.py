#! /usr/bin/python3
import multiprocessing as mp

from src.args import args
from src.utils import random
from src.modules.Executor import Executor


def run(i):
    random.r.seed()
    executor = Executor(i, args)
    return executor.process_program()

pool = mp.Pool(args.workers)
pool.map(run, list(range(1, args.iterations + 1)))
pool.close()
pool.join()
