#! /usr/bin/env python3
import csv
import argparse
from collections import defaultdict


def get_args():
    parser = argparse.ArgumentParser(
        description='Compute coverage'
    )
    parser.add_argument("testsuite", help="CSV for test suite")
    parser.add_argument("generator", help="CSV for combination")
    parser.add_argument("combination", help="CSV for combination")
    parser.add_argument("whitelist",
                        help="Whitelist of packages we should include.")
    return parser.parse_args()


def check_pkg(pkg, whitelist):
    for pattern in whitelist:
        if '*' in pattern and pkg.startswith(pattern[:-1]):
            return True
        if pkg == pattern:
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
            if check_pkg(pkg, whitelist):
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

def print_perc(pkg, res, metric):
    print("{:<70}{:>5.2f}".format(pkg, compute_perc(res, metric)))

def print_res(testsuite, generator, comb):
    #for pkg, res in comb.items():
    #    if pkg == 'total':
    #        continue
    #    print_perc(pkg, res, 'branch')
    #print_perc('total', comb['total'], 'branch')
    template = "{:<20} {:>18} {:>18} {:>18}"
    template_f = "{:<20} {:>18.2f} {:>18.2f} {:>18.2f}"
    print(template.format(
        "", "Line Coverage", "Function Coverage", "Branch Coverage"
    ))
    ts_pers_line = compute_perc(testsuite['total'], 'line')
    ts_pers_function = compute_perc(testsuite['total'], 'function')
    ts_pers_branch = compute_perc(testsuite['total'], 'branch')
    generator_pers_line = compute_perc(generator['total'], 'line')
    generator_pers_function = compute_perc(generator['total'], 'function')
    generator_pers_branch = compute_perc(generator['total'], 'branch')
    comb_pers_line = compute_perc(comb['total'], 'line')
    comb_pers_function = compute_perc(comb['total'], 'function')
    comb_pers_branch = compute_perc(comb['total'], 'branch')
    print(template_f.format(
        "Test suite",
        ts_pers_line,
        ts_pers_function,
        ts_pers_branch
    ))
    print(template_f.format(
        "Generator",
        generator_pers_line,
        generator_pers_function,
        generator_pers_branch
    ))
    print(template_f.format(
        "Combination",
        comb_pers_line,
        comb_pers_function,
        comb_pers_branch,
    ))
    print(template_f.format(
        "% change",
        comb_pers_line - ts_pers_line,
        comb_pers_function - ts_pers_function,
        comb_pers_branch - ts_pers_branch,
    ))
    print(template.format(
        "absolute change",
        compute_abs_diff(comb['total'], testsuite['total'], 'line'),
        compute_abs_diff(comb['total'], testsuite['total'], 'function'),
        compute_abs_diff(comb['total'], testsuite['total'], 'branch')
    ))


def main():
    args = get_args()

    with open(args.whitelist) as f:
        whitelist = [l.strip() for l in f.readlines()]

    testsuite = read_csv(args.testsuite, whitelist)
    generator = read_csv(args.generator, whitelist)
    comb = read_csv(args.combination, whitelist)
    print_res(testsuite, generator, comb)



if __name__ == "__main__":
    main()
