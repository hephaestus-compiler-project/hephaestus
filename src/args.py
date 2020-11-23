import argparse
import os
import sys
from src.utils import random_string, mkdir


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
    "-r", "--rounds",
    type=int,
    default=10,
    help="Number of rounds in each iteration"
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
    default=random_string(),
    help="Set name of this testing instance (default: random string)"
)
args = parser.parse_args()

# CHECK ARGUMENTS

if not args.seconds and not args.iterations:
    args.iterations = 3

if args.seconds and args.iterations:
    sys.exit("Error: you should only set --seconds or --iterations")

if os.path.isdir(args.bugs) and args.name in os.listdir(args.bugs):
    sys.exit("Error: --name {} already exists".format(args.name))

# PRE-PROCESSING

if not os.path.isdir(args.bugs):
    mkdir(args.bugs)

args.test_directory = os.path.join(args.bugs, args.name)
if not os.path.isdir(args.test_directory):
    mkdir(args.test_directory)

args.stop_cond = "timeout" if args.seconds else "number"
args.temp_directory = os.path.join(cwd, "temp")

# LOGGING
print("{} {} ({})".format("stop_cond".ljust(16), args.stop_cond,
                          args.seconds if args.stop_cond == "timeout" else args.iterations))
print("{} {}".format("rounds".ljust(16), args.rounds))
print("{} {}".format("transformations".ljust(16), args.transformations))
print("{} {}".format("bugs".ljust(16), args.bugs))
print("{} {}".format("name".ljust(16), args.name))
