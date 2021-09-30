import argparse
import json
from collections import defaultdict


def get_args():
    parser = argparse.ArgumentParser(
        description='Compute statistics for the bugs.')
    parser.add_argument("input", help="File with bugs.")
    return parser.parse_args()


def print_stats(lang, stats):
    print(80*"=")
    total = sum(v for v in stats['oracle'].values())
    print(lang + ' (total:' + str(total) + ')')
    print(80*"-")
    for category, value in stats.items():
        value = {k if k else "None": v for k, v in value.items()}
        res = [k + " (" + str(v) + ")" for k,v in value.items()]
        print("{}: {}".format(category, ", ".join(res)), )
    print(80*"=")


def main():
    args = get_args()
    with open(args.input, 'r') as f:
        data = json.load(f)
    stats = defaultdict(lambda: {
        'oracle': defaultdict(lambda: 0),
        'mutator': defaultdict(lambda: 0),
        'status': defaultdict(lambda: 0),
        'resolution': defaultdict(lambda: 0),
        'symptom': defaultdict(lambda: 0),
    })
    for bug in data:
        for key in ('oracle', 'mutator', 'status', 'resolution', 'symptom'):
            stats[bug['compiler']][key][bug[key]] += 1
            stats['total'][key][bug[key]] += 1
    total = None
    for lang, values in stats.items():
        if lang == "total":
            total = values
        else:
            print_stats(lang, values)
    print_stats("total", total)


if __name__ == "__main__":
    main()
