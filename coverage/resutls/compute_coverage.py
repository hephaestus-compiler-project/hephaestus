#! /usr/bin/env python3
import csv
import argparse
from collections import defaultdict


def get_args():
    parser = argparse.ArgumentParser(
        description='Compute coverage'
    )
    parser.add_argument("lang", help="language")
    parser.add_argument("testsuite", help="CSV for test suite")
    parser.add_argument("generator", help="CSV for combination")
    parser.add_argument("combination", help="CSV for combination")
    parser.add_argument("whitelist",
                        help="Whitelist of packages we should include.")
    parser.add_argument("--latex", action="store_true")
    parser.add_argument("--inf", action="store_true")
    parser.add_argument("--increasepkg", action="store_true")
    parser.add_argument("--increasecls", action="store_true")
    return parser.parse_args()


def check(pkg, cls, whitelist):
    def check_pkg(pattern):
        if '*' in pattern and pkg.startswith(pattern[:-1]):
            return True
        if pkg == pattern:
            return True

    for pattern in whitelist:
        if ',' not in pattern and check_pkg(pattern):
            return True
        elif ',' in pattern:
            pkg = pattern.split(',')[0]
            cls2 = pattern.split(',')[1]
            if cls.startswith(cls2):
                return True
    return False


def read_csv(name, whitelist):
    res = defaultdict(lambda: defaultdict(lambda: 0))
    with open(name, 'r') as f:
        csvreader = csv.reader(f)
        next(csvreader)
        # Header
        # (0) GROUP,(1) PACKAGE,(2) CLASS,
        # (3)INSTRUCTION_MISSED, (4)INSTRUCTION_COVERED,
        # (5)BRANCH_MISSED, (6)BRANCH_COVERED,
        # (7)LINE_MISSED, (8)LINE_COVERED,
        # (9)COMPLEXITY_MISSED, (10)COMPLEXITY_COVERED,
        # (11)METHOD_MISSED, (12)METHOD_COVERED

        for row in csvreader:
            pkg = row[1]
            cls = row[2]
            if check(pkg, cls, whitelist):
                branch_missed = row[3]
                branch_covered = row[4]
                line_missed = row[7]
                line_covered = row[8]
                function_missed = row[11]
                function_covered = row[12]
                res[pkg]['branch_missed'] += int(branch_missed)
                res[pkg]['branch_covered'] += int(branch_covered)
                res[pkg]['line_missed'] += int(line_missed)
                res[pkg]['line_covered'] += int(line_covered)
                res[pkg]['function_missed'] += int(function_missed)
                res[pkg]['function_covered'] += int(function_covered)
                res[(pkg, cls)]['branch_missed'] += int(branch_missed)
                res[(pkg, cls)]['branch_covered'] += int(branch_covered)
                res[(pkg, cls)]['line_missed'] += int(line_missed)
                res[(pkg, cls)]['line_covered'] += int(line_covered)
                res[(pkg, cls)]['function_missed'] += int(function_missed)
                res[(pkg, cls)]['function_covered'] += int(function_covered)
                res['total']['branch_missed'] += int(branch_missed)
                res['total']['branch_covered'] += int(branch_covered)
                res['total']['line_missed'] += int(line_missed)
                res['total']['line_covered'] += int(line_covered)
                res['total']['function_missed'] += int(function_missed)
                res['total']['function_covered'] += int(function_covered)
    return res


def compute_perc(res, metric):
    covered = metric + '_covered'
    covered = res[covered]
    missed = metric + '_missed'
    missed = res[missed]
    if covered == 0 and missed == 0:
        return 0
    return (covered / (covered + missed)) * 100


def compute_abs_diff(res1, res2, metric):
    covered = metric + '_covered'
    covered1 = res1[covered]
    covered2 = res2[covered]
    return covered1 - covered2


def print_latex_command(lang, category, d, inf):
    template = "\\newcommand{{\\{lang}cov{inf}{category}{metric}}}{{\\nnum{{{num}}}}}"
    for k, v in d.items():
        v="{:.2f}".format(v) if isinstance(v, float) else v
        print(template.format(
            lang=lang,
            category=category,
            inf="inf" if inf else "",
            metric=k,
            num=v
        ))


def get_dict_format(line, function, branch):
    return {"line": line, "function": function, "branch": branch}


def print_dict(name, d, template):
    print(template.format(name, d['line'], d['function'], d['branch']))


def print_res(lang, testsuite, generator, comb, latex, inf):
    template = "{:<20} {:>18} {:>18} {:>18}"
    template_f = "{:<20} {:>18.2f} {:>18.2f} {:>18.2f}"
    print(template.format(
        "", "Line Coverage", "Function Coverage", "Branch Coverage"
    ))
    ts_dict = get_dict_format(
        compute_perc(testsuite['total'], 'line'),
        compute_perc(testsuite['total'], 'function'),
        compute_perc(testsuite['total'], 'branch'))
    generator_dict = get_dict_format(
        compute_perc(generator['total'], 'line'),
        compute_perc(generator['total'], 'function'),
        compute_perc(generator['total'], 'branch'))
    comb_dict = get_dict_format(
        compute_perc(comb['total'], 'line'),
        compute_perc(comb['total'], 'function'),
        compute_perc(comb['total'], 'branch'))
    change_dict = get_dict_format(
        comb_dict['line'] - ts_dict['line'],
        comb_dict['function'] - ts_dict['function'],
        comb_dict['branch'] - ts_dict['branch'])
    abs_dict = get_dict_format(
        compute_abs_diff(comb['total'], testsuite['total'], 'line'),
        compute_abs_diff(comb['total'], testsuite['total'], 'function'),
        compute_abs_diff(comb['total'], testsuite['total'], 'branch'))
    print_dict("Test Suite", ts_dict, template_f)
    print_dict("Generator", generator_dict, template_f)
    print_dict("Combination", comb_dict, template_f)
    print_dict("% change", change_dict, template_f)
    print_dict("Absolute change", abs_dict, template)
    if latex:
        categories = [
            ('test', ts_dict),
            ('gen', generator_dict),
            ('comb', comb_dict),
            ('change', change_dict),
            ('abs', abs_dict)
        ]
        for category, d in categories:
            print_latex_command(lang, category, d, inf)


def compute_increase(res1, res2, cls=False):
    res3 = defaultdict(lambda: defaultdict(lambda: 0))
    for pkg in res2.keys():
        if not cls and isinstance(pkg, tuple):
            continue
        if cls and not isinstance(pkg, tuple):
            continue
        increase = res2[pkg]['branch_covered'] - res1[pkg]['branch_covered']
        perc_incr = 0
        if res1[pkg]['branch_covered'] > 0:
            perc_incr =  (increase / res1[pkg]['branch_covered']) * 100
        elif res2[pkg]['branch_covered'] > 0:
            perc_incr = 9999999
        if perc_incr <= 0:
            continue
        res3[pkg]['branch_covered'] = increase
        res3[pkg]['branch_perc'] = perc_incr
    return res3

def main():
    args = get_args()

    with open(args.whitelist) as f:
        whitelist = [l.strip() for l in f.readlines()]

    testsuite = read_csv(args.testsuite, whitelist)
    generator = read_csv(args.generator, whitelist)
    comb = read_csv(args.combination, whitelist)
    print_res(args.lang, testsuite, generator, comb, args.latex, args.inf)

    if args.increasepkg or args.increasecls:
        increase = compute_increase(testsuite, comb, args.increasecls)
        increase_view = [(
            v['branch_perc'], 
            (k[0] + "," + k[1] if isinstance(k, tuple) else k, 
            v['branch_covered']))
            for k,v in increase.items() ]
        increase_view.sort(reverse=True)
        for view in increase_view:
            print("{name}: {absolute} ({percentage})".format(
                name=view[1][0],
                absolute=view[1][1],
                percentage=view[0]
            ))



if __name__ == "__main__":
    main()
