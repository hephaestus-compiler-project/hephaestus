#! /usr/bin/python3

from src.args import args
from src.modules.Executor import Executor

executor = Executor(args)
executor.run()
