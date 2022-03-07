import argparse
import json
from collections import defaultdict


features_lookup = {
    "Parameterized class": "Parametric polymorphism",
    "Parameterized type": "Parametric polymorphism",
    "Parameterized function": "Parametric polymorphism",
    "Use-site variance": "Parametric polymorphism",
    "Bounded type parameter": "Parametric polymorphism",
    "Declaration-site variance": "Parametric polymorphism",
    "Inheritance": "OOP features",
    "Overriding": "OOP features",
    "Subtyping": "Type system-related features",
    "Primitive type": "Type system-related features",
    "Wildcard type": "Type system-related features",
    "Nothing": "Type system-related features",
    "Lambda": "Functional programming",
    "Function reference": "Functional programming",
    "SAM type": "Functional programming",
    "Function type": "Functional programming",
    "Conditionals": "Standard language features",
    "Array": "Standard language features",
    "Cast": "Standard language features",
    "Variable arguments": "Standard language features",
    "Type argument inference": "Type inference",
    "Variable type inference": "Type inference",
    "Parameter type inference": "Type inference",
    "Flow typing": "Type inference",
    "Return type inference": "Type inference",
    "Named arguments": "Other"
}


def get_args():
    parser = argparse.ArgumentParser(
        description='Compute statistics for the bugs.')
    parser.add_argument("input", help="File with bugs.")
    parser.add_argument("--latex", action='store_true', 
                        help='Print latex commands')
    parser.add_argument("--combinations", action='store_true', 
                        help='Print chars combinations')
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

def print_chars(chars_view):
    print()
    print(80*"=")
    print("Characteristics")
    print(80*"-")
    for count, char in chars_view:
        print("{:<29}{:<5}{:<50}".format(char, count, features_lookup[char]))
    print(80*"=")


def print_feature_chars(feature_chars_view):
    print()
    print(80*"=")
    print("Feature Categories")
    print(80*"-")
    for count, char in feature_chars_view:
        print("{:<50}{:<5}".format(char, count))
    print(80*"=")


def print_latex_commands(lang, stats, chars_view, feature_chars_view):
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
    if lang == 'Total':
        real_bugs = stats['status']['Confirmed'] + stats['status']['Fixed']
        print(template.format(
            lang='t',
            category='real',
            num=real_bugs
        ))
    print(template.format(
        lang=lookup.get(lang, lang),
        category='total',
        num=total
    ))
    print()
    print()
    for count, char in chars_view:
        char = char.replace(' ', '').replace('-', '').lower()
        char = 'llambda' if char == 'lambda' else char
        char = 'aarray' if char == 'array' else char
        print(template.format(
            lang="",
            category=char,
            num=count
        ))
    print()
    for count, char in feature_chars_view:
        char = char.replace(' ', '').replace('-', '').lower()
        print(template.format(
            lang="",
            category=char,
            num=count
        ))


def process(bug, res, chars, feature_chars, combinations):
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
                'Answered': 'Confirmed',
                'Duplicate': 'Duplicate'
            },
            'Groovy': {
                'Duplicate': 'Duplicate', 
                'Information Provided': 'Wont fix',
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

    feature_categories = set()
    for char in bug['chars']['characteristics']:
        chars[char] += 1
        feature_categories.add(features_lookup[char])
        categories = set()
        for comb in bug['chars']['characteristics']:
            if char != comb:
                categories.add(features_lookup[comb])
        for cat in categories:
            combinations[char][cat] += 1
    for char in feature_categories:
        feature_chars[char] += 1


def main():
    args = get_args()
    with open(args.input, 'r') as f:
        data = json.load(f)
    chars = defaultdict(lambda: 0)
    feature_chars = defaultdict(lambda: 0)
    combinations = defaultdict(lambda: defaultdict(lambda: 0))
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
        process(bug, res, chars, feature_chars, combinations)
    total = None
    for lang, values in res.items():
        if lang == "total":
            total = values
        else:
            print_stats(lang, values)
    print_stats("total", total)

    chars_view = [ (v,k) for k,v in chars.items() ]
    chars_view.sort(reverse=True)
    print_chars(chars_view)

    feature_chars_view = [ (v,k) for k,v in feature_chars.items() ]
    feature_chars_view.sort(reverse=True)
    print_feature_chars(feature_chars_view)

    if args.latex:
        total = None
        for lang, values in res.items():
            if lang == "total":
                total = values
            else:
                print_latex_commands(lang, values, [], [])
        print_latex_commands("Total", total, chars_view, feature_chars_view)

    if args.combinations:
        for char, combs in combinations.items():
            for comb, value in combs.items():
                print("{:<29} {:<29} {:>5}".format(char, comb, value))

if __name__ == "__main__":
    main()
