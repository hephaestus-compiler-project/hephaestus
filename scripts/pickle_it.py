import pickle
import argparse
import importlib
import os
import sys


sys.path.insert(0, os.getcwd())
example_usage = '''example:

  python pickle_it.py "src.examples.kt_15706" kt_15706.bin'''

parser = argparse.ArgumentParser(
    description='Pickle a program.',
    epilog=example_usage
)
parser.add_argument('program', help='Python module with the program')
parser.add_argument('output', help='Filename to save the pickled program')
args = parser.parse_args()

pmodule =  importlib.import_module(args.program)
program = pmodule.program
with open(args.output, "wb") as out:
    pickle.dump(program, out)
