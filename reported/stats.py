import argparse
import json
from collections import defaultdict


def get_args():
    parser = argparse.ArgumentParser(
        description='Compute statistics for the bugs.')
    parser.add_argument("input", help="File with bugs.")
    return parser.parse_args()


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
    for lang, values in stats.items():
        print(80*"=")
        total = sum(v for v in values['oracle'].values())
        print(lang + ' (total:' + str(total) + ')')
        print(80*"-")
        for category, value in values.items():
            value = {k if k else "None": v for k, v in value.items()}
            res = [k + " (" + str(v) + ")" for k,v in value.items()]
            print("{}: {}".format(category, ", ".join(res)), )
        print(80*"=")


if __name__ == "__main__":
    main()
