import argparse
import os
import sys
from src.utils import random, mkdir
from src.modules.processor import ProgramProcessor


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
    default=None,
    help="Number of transformations in each round"
)
parser.add_argument(
    "--batch",
    type=int,
    default=1,
    help='Number of programs to generate before invoking the compiler'
)
parser.add_argument(
    "-b", "--bugs",
    default=os.path.join(cwd, "bugs"),
    help="Set bug directory (default: " + str(os.path.join(cwd, "bugs")) + ")"
)
parser.add_argument(
    "-n", "--name",
    default=random.str(),
    help="Set name of this testing instance (default: random string)"
)
parser.add_argument(
    "-T", "--transformation-types",
    default=ProgramProcessor.TRANSFORMATIONS.keys(),
    nargs="*",
    choices=ProgramProcessor.TRANSFORMATIONS.keys(),
    help="Select specific transformations to perform"
)
parser.add_argument(
    "--transformation-schedule",
    default=None,
    type=str,
    help="A file containing the schedule of transformations"
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
    "--disable-inference-in-closures",
    default=True,
    action="store_true",
    help="Generate closures that have an explicit return type"
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
    default=None,
    help="Number of workers for processing test programs"
)
parser.add_argument(
    "-d", "--debug",
    action="store_true"
)
parser.add_argument(
    "-r", "--rerun",
    action="store_true",
    help=("Run only the last transformation. If failed, start from the last "
          "and go back until the transformation introduces the error")
)
parser.add_argument(
    "-F", "--log-file",
    default=os.path.join(cwd, "logs"),
    help="Set log file (default: " + str(os.path.join(cwd, "logs")) + ")"
)
parser.add_argument(
    "-L", "--log",
    action="store_true",
    help="Keep logs for each transformation (bugs/session/logs)"
)
parser.add_argument(
    "-N", "--dry-run",
    action="store_true",
    help="Do not compile the programs"
)
parser.add_argument(
    "--language",
    default="kotlin",
    nargs="*",
    choices=['kotlin'],
    help="Select specific language"
)


args = parser.parse_args()


# CHECK ARGUMENTS

if args.seconds and args.iterations:
    sys.exit("Error: you should only set --seconds or --iterations")

if os.path.isdir(args.bugs) and args.name in os.listdir(args.bugs):
    sys.exit("Error: --name {} already exists".format(args.name))

if args.transformation_schedule and args.transformations:
    sys.exit("Options --transformation-schedule and --transfromations"
             " are mutually exclusive. You can't use both.")

if not args.transformation_schedule and not args.transformations:
    sys.exit("You have to provide one of --transformation-schedule or"
             " --transformations.")

if args.transformation_schedule and (
        not os.path.isfile(args.transformation_schedule)):
    sys.exit("You have to provide a valid file in --transformation-schedule")


if args.rerun and args.workers:
    sys.exit('You cannot use -r option in parallel mode')


if args.rerun and not args.keep_all:
    sys.exit("The -r option only works with the option -k")


# PRE-PROCESSING

if not os.path.isdir(args.bugs):
    mkdir(args.bugs)

args.test_directory = os.path.join(args.bugs, args.name)

args.stop_cond = "timeout" if args.seconds else "iterations"
args.temp_directory = os.path.join(cwd, "temp")
