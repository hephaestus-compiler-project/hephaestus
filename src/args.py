import argparse
import os
import sys
from src.utils import random, mkdir, fprint
from src.modules.Executor import Executor


cwd = os.getcwd()

parser = argparse.ArgumentParser()
parser.add_argument(
    "-s", "--seconds",
    type=int,
    help="Timeout in seconds"
)
parser.add_argument(
    "-i", "--iterations",
    type=int,
    help="Iterations to run (default: 3)"
)
parser.add_argument(
    "-t", "--transformations",
    type=int,
    default=5,
    help="Number of transformations in each round"
)
parser.add_argument(
    "-b", "--bugs",
    default=cwd + "/bugs",
    help="Set bug directory (default: " + cwd + "/bugs)"
)
parser.add_argument(
    "-n", "--name",
    default=random.str(),
    help="Set name of this testing instance (default: random string)"
)
parser.add_argument(
    "-T", "--transformation-types",
    default=Executor.TRANSFORMATIONS.keys(),
    nargs="*",
    choices=Executor.TRANSFORMATIONS.keys(),
    help="Select specific transformations to perform"
)
parser.add_argument(
    "-R", "--replay",
    help="Give a program to use instead of a randomly generated (pickled)"
)
parser.add_argument(
    "-k", "--keep-all",
    action="store_true",
    help="Save all programs"
)
parser.add_argument(
    "--max-depth",
    type=int,
    default=7,
    help="Max depth of generated programs"
)
parser.add_argument(
    "-S", "--print-stacktrace",
    action="store_true",
    help="When an error occurs print stack trace"
)
parser.add_argument(
    "-w", "--workers",
    type=int,
    default=1,
    help="Number of workers for processing test programs"
)
parser.add_argument(
    "-l", "--only-last",
    action="store_true",
    help="Test only the last transformation"
)
parser.add_argument(
    "-d", "--debug",
    action="store_true"
)
parser.add_argument(
    "-r", "--rerun",
    action="store_true",
    help=("Run only the last transformation. If failed, start from the last "
          "and goes back until the transformation introduces the error")
)


args = parser.parse_args()

# CHECK ARGUMENTS

if not args.seconds and not args.iterations:
    args.iterations = 3

if args.seconds and args.iterations:
    sys.exit("Error: you should only set --seconds or --iterations")

if os.path.isdir(args.bugs) and args.name in os.listdir(args.bugs):
    sys.exit("Error: --name {} already exists".format(args.name))

if sum(1 for i in (args.rerun, args.debug) if i is True) > 1:
    sys.exit("Error: You can use only one of -r, -d.")

# PRE-PROCESSING

if not os.path.isdir(args.bugs):
    mkdir(args.bugs)

args.test_directory = os.path.join(args.bugs, args.name)

args.stop_cond = "timeout" if args.seconds else "number"
args.temp_directory = os.path.join(cwd, "temp")

# LOGGING
print("{} {} ({})".format("stop_cond".ljust(21), args.stop_cond,
                          args.seconds if args.stop_cond == "timeout" else args.iterations))
print("{} {}".format("transformations".ljust(21), args.transformations))
print("{} {}".format("transformation_types".ljust(21), ",".join(args.transformation_types)))
print("{} {}".format("bugs".ljust(21), args.bugs))
print("{} {}".format("name".ljust(21), args.name))
fprint("")
