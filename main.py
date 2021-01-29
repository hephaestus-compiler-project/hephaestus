#! /usr/bin/python3
# pylint: disable=global-statement
from src.args import args
from src.modules.test_runner import run, run_parallel


def main():
    if args.debug or args.workers is None:
        run()
    else:
        run_parallel()


if __name__ == "__main__":
    main()
