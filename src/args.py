import argparse
import os
import sys
from src.utils import random, mkdir
from src.modules.processor import ProgramProcessor
from src.generators.config import cfg


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
    default=0,
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
    default=ProgramProcessor.CP_TRANSFORMATIONS.keys(),
    nargs="*",
    choices=ProgramProcessor.CP_TRANSFORMATIONS.keys(),
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
    "-e", "--examine",
    action="store_true",
    help="Open ipdb for a program (can be used only with --replay option)"
)
parser.add_argument(
    "-k", "--keep-all",
    action="store_true",
    help="Save all programs"
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
    choices=['kotlin', 'groovy', 'java', 'typescript'],
    help="Select specific language"
)
parser.add_argument(
    "--max-type-params",
    type=int,
    default=3,
    help="Maximum number of type parameters to generate"
)
parser.add_argument(
    "--max-depth",
    type=int,
    default=6,
    help="Generate programs up to the given depth"
)
parser.add_argument(
    "-P",
    "--only-correctness-preserving-transformations",
    action="store_true",
    help="Use only correctness-preserving transformations"
)
parser.add_argument(
    "--timeout",
    type=int,
    default=600,
    help="Timeout for transformations (in seconds)"
)
parser.add_argument(
    "--cast-numbers",
    action="store_true",
    help=("Cast numeric constants to their actual type"
          " (this option is used to avoid re-occrrence of"
          " a specific Groovy bug)")
)
parser.add_argument(
    "--disable-use-site-variance",
    action="store_true",
    help="Disable use-site variance"
)
parser.add_argument(
    "--disable-contravariance-use-site",
    action="store_true",
    help="Disable contravariance in use-site variance"
)
parser.add_argument(
    "--disable-bounded-type-parameters",
    action="store_true",
    help="Disable bounded type parameters"
)
parser.add_argument(
    "--disable-parameterized-functions",
    action="store_true",
    help="Disable parameterized functions"
)
parser.add_argument(
    "--error-filter-patterns",
    default='',
    type=str,
    help=("A file containing regular expressions for filtering compiler error "
          "messages")
)


args = parser.parse_args()


args.test_directory = os.path.join(args.bugs, args.name)
args.stop_cond = "timeout" if args.seconds else "iterations"
args.temp_directory = os.path.join(cwd, "temp")
args.options = {
    "Generator": {
    },
    'Translator': {
        'cast_numbers': args.cast_numbers,
    },
    "TypeErasure": {
        "timeout": args.timeout
    },
    "TypeOverwriting": {
        "timeout": args.timeout
    }
}
random.remove_reserved_words(args.language)


# Set configurations

cfg.dis.use_site_variance = args.disable_use_site_variance
cfg.dis.use_site_contravariance = args.disable_contravariance_use_site
cfg.limits.max_depth = args.max_depth
if args.disable_bounded_type_parameters:
    cfg.prob.bounded_type_parameters = 0
if args.disable_parameterized_functions:
    cfg.prob.parameterized_functions = 0


def validate_args(args):
    # CHECK ARGUMENTS

    if args.seconds and args.iterations:
        sys.exit("Error: you should only set --seconds or --iterations")

    if os.path.isdir(args.bugs) and args.name in os.listdir(args.bugs):
        sys.exit("Error: --name {} already exists".format(args.name))

    if args.transformation_schedule and args.transformations:
        sys.exit("Options --transformation-schedule and --transfromations"
                 " are mutually exclusive. You can't use both.")

    if not args.transformation_schedule and args.transformations is None:
        sys.exit("You have to provide one of --transformation-schedule or"
                 " --transformations.")

    if args.transformation_schedule and (
            not os.path.isfile(args.transformation_schedule)):
        sys.exit("You have to provide a valid file in --transformation-schedule")

    if args.rerun and args.workers:
        sys.exit('You cannot use -r option in parallel mode')

    if args.rerun and not args.keep_all:
        sys.exit("The -r option only works with the option -k")

    if args.rerun and args.batch:
        sys.exit("You cannot use -r option with the option --batch")

    if args.examine and not args.replay:
        sys.exit("You cannot use --examine option without the --replay option")

    if args.language == "typescript" and not args.disable_use_site_variance:
        sys.exit("\nTypeScript does not have use-site variance.\nRun Hephaestus again with the flag --disable-use-site-variance.")


def pre_process_args(args):
    # PRE-PROCESSING

    if not os.path.isdir(args.bugs):
        mkdir(args.bugs)
