import argparse
import json
from collections import defaultdict


def get_args():
    parser = argparse.ArgumentParser(
        description='Compute statistics for the bugs.')
    parser.add_argument("input", help="File with bugs.")
    parser.add_argument("--latex", action='store_true', 
                        help='Print latex commands')
    return parser.parse_args()


def print_stats(lang, stats):
    print(80*"=")
    total = sum(v for v in stats['status'].values())
    print(lang + ' (total:' + str(total) + ')')
    print(80*"-")
    for category, value in stats.items():
        value = {k if k else "None": v for k, v in value.items()}
        res = [k + " (" + str(v) + ")" for k,v in value.items()]
        print("{}: {}".format(category, ", ".join(res)))
        print(80*"=")


def print_latex_commands(lang, stats):
    template = "\\newcommand{{\\{lang}{category}}}{{\\nnum{{{num}}}}}"
    lookup = {
            'Java': 'j',
            'Groovy': 'g',
            'Kotlin': 'k',
            'Total': 't',
            'Reported': 'report',
            'Confirmed': 'confirmed',
            'Fixed': 'fix',
            'Duplicate': 'dupl',
            'Wont fix': 'wont',
            'Unexpected Compile-Time Error': 'ucte',
            'Unexpected Runtime Behavior': 'urb',
            'inference/soundness': 'comb'
    }
    total = sum(v for v in stats['status'].values())
    for category, value in stats.items():
        value = {k if k else "None": v for k, v in value.items()}
        for k, v in value.items():
            print(template.format(
                lang=lookup.get(lang, lang),
                category=lookup.get(k, k),
                num=v
            ))
        print()
    print(template.format(
        lang=lookup.get(lang, lang),
        category='total',
        num=total
    ))
    print()



def process(bug, res):
    d = {
        'status': {
            'Kotlin': {
                'Submitted': 'Reported',
                'In Progress': 'Confirmed',
                'Open': 'Confirmed',
                'Closed': None
            },
            'Groovy': {
                'Open': 'Confirmed',
                'In Progress': 'Confirmed',
                'Resolved': None,
                'Closed': None
            },
            'Java': {
                'New': 'Confirmed',
                'Closed': None,
                'Resolved': None,
                'Open': 'Confirmed'
            }
        },
        'resolution': {
            'Kotlin': {
                'Fixed': 'Fixed', 
                'Obsolete': 'Confirmed', 
                'As Designed': 'Wont fix',
                'Duplicate': 'Duplicate'
            },
            'Groovy': {
                'Duplicate': 'Duplicate', 
                'Fixed': 'Fixed'
            },
            'Java': {
                'Not an Issue':  'Wont fix', 
                'Duplicate': 'Duplicate', 
                'Fixed': 'Fixed'
            }
        },
        'symptom': {
            'Unexpected Compile-Time Error': 'Unexpected Compile-Time Error', 
            'Unexpected Runtime Behavior': 'Unexpected Runtime Behavior',
            'crash': 'crash', 
            'Misleading Report': 'Unexpected Compile-Time Error'
        },
    }
    lang = bug['language']
    bstatus = bug['status']
    bresolution = bug['resolution']
    bsymptom = bug['symptom']
    bmutator = bug['mutator']
    status = d['status'][lang].get(bstatus, None)
    if status is None:
        status = d['resolution'][lang].get(bresolution, None)
    symptom = d['symptom'].get(bsymptom, None)
    res[lang]['status'][status] += 1
    res[lang]['symptom'][symptom] += 1
    res[lang]['mutator'][bmutator] += 1
    res['total']['status'][status] += 1
    res['total']['symptom'][symptom] += 1
    res['total']['mutator'][bmutator] += 1


def main():
    args = get_args()
    with open(args.input, 'r') as f:
        data = json.load(f)
    res = defaultdict(lambda: {
        'status': {
            'Reported': 0,
            'Confirmed': 0,
            'Fixed': 0,
            'Wont fix': 0,
            'Duplicate': 0
        },
        'symptom': {
            'crash': 0,
            'Unexpected Compile-Time Error': 0,
            'Unexpected Runtime Behavior': 0
        },
        'mutator': {
            'generator': 0,
            'soundness': 0,
            'inference': 0,
            'inference/soundness': 0
        }
    })
    for bug in data:
        process(bug, res)
    total = None
    for lang, values in res.items():
        if lang == "total":
            total = values
        else:
            print_stats(lang, values)
    print_stats("total", total)

    if args.latex:
        total = None
        for lang, values in res.items():
            if lang == "total":
                total = values
            else:
                print_latex_commands(lang, values)
        print_latex_commands("Total", total)

if __name__ == "__main__":
    main()
