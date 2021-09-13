#! /usr/bin/env python3
import csv
import argparse


GENERATOR = "generator"
SOUNDNESS = "soundness"
INFERENCE = "inference"


def get_branches(branches, declarations, stage):
    return {b for b in branches if declarations[b]['primary'] == stage}


def get_dbranches(declarations, stage):
    return {b for b, v in declarations.items() if v['primary'] == stage}


def print_stats(title, branches, total):
    print("{}: {}% ({}/{})".format(
        title, int((branches / total)*100), branches, total
    ))

def get_args():
    parser = argparse.ArgumentParser(
        description='Compute coverage'
    )
    parser.add_argument("branches", help="File with branch declarations")
    parser.add_argument("data", help="File with coverage data")
    parser.add_argument(
        "--generator",
        action="store_true",
        help="Show missing branches (generator)"
    )
    parser.add_argument(
        "--inference",
        action="store_true",
        help="Show missing branches (inference)"
    )
    return parser.parse_args()


def main():
    args = get_args()
    declarations = {}

    with open(args.branches, 'r') as f:
        csvreader = csv.reader(f)
        next(csvreader)
        for row in csvreader:
            declarations[row[0]] = {
                    "file": row[1],
                    "method": row[2],
                    "primary": row[3].split(';')[0],
                    "description": row[4]
            }

    with open(args.data, 'r') as f:
        branches = {line.rstrip() for line in f.readlines()}

    generator = get_branches(branches, declarations, GENERATOR)
    soundness = get_branches(branches, declarations, SOUNDNESS)
    inference = get_branches(branches, declarations, INFERENCE)

    dgenerator = get_dbranches(declarations, GENERATOR)
    dsoundness = get_dbranches(declarations, SOUNDNESS)
    dinference = get_dbranches(declarations, INFERENCE)

    print(20*"=")
    print_stats("Total", len(branches), len(set(declarations.keys())))
    print_stats("Generator", len(generator), len(dgenerator))
    print_stats("Soundness", len(soundness), len(dsoundness))
    print_stats("Inference", len(inference), len(dinference))
    print(20*"=")

    if args.generator:
        print()
        print("Generator: {}".format(
            dgenerator - generator
        ))

    if args.inference:
        print()
        print("Inference: {}".format(
            dinference - inference
        ))

if __name__ == "__main__":
    main()
