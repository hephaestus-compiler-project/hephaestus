#! /usr/bin/env python3
import argparse
import json

from collections import defaultdict

import kotlin as kt
import java as jv
import scala as sc
import groovy as gv

from characteristics import CharacteristicCategory


def get_args():
    parser = argparse.ArgumentParser(
        description='Serialize bugs.')
    parser.add_argument("output", help="File to save the bugs.")
    parser.add_argument(
        "characteristics",
        help="File to save bug characteristics distribution.")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    bugs = jv.java_iter1 + jv.java_iter2 + jv.java_iter3 + jv.java_iter4 + \
        sc.scala_iter1 + sc.scala_iter2 + sc.scala_iter3 + sc.scala_iter4 + \
        kt.kotlin_iter1 + kt.kotlin_iter2 + kt.kotlin_iter3 + kt.kotlin_iter4 + \
        gv.groovy_iter1 + gv.groovy_iter2 + gv.groovy_iter3 + gv.groovy_iter4
    res = {}
    char_stats = {
            "Categories": defaultdict(
                lambda: {"total": 0,
                         "subcategories": defaultdict(
                             lambda: {"total": 0,
                                      "subcategories": defaultdict(
                                          lambda: 0)})}),
            "Types": defaultdict(lambda: 0),
            "Commons": {"True": 0, "False": 0}}
    for b in bugs:
        # bug id
        bug_id = b.bug_id.split('.')[-1] if '.' in b.bug_id else b.bug_id
        # characteristics
        chars = {"characteristics": set(), "categories": set()}
        visited = set()
        for c in b.characteristics:
            chars["characteristics"].add(c.name)
            if c.category is not None:
                chars["categories"].add(c.category.name)
            # Characteristics distribution
            if isinstance(c.category, CharacteristicCategory):
                cat = char_stats["Categories"][c.category.name]
                if c.category.name not in visited:
                    cat["total"] += 1
                    visited.add(c.category.name)
                cat["subcategories"][c.name]["total"] += 1
                cat["subcategories"][c.name]["is_common"] = c.is_common
            else:
                cat = char_stats["Categories"][c.category.category.name]
                if c.category.category.name not in visited:
                    cat["total"] += 1
                    visited.add(c.category.category.name)
                cat["subcategories"][c.category.name]["total"] += 1
                cat["subcategories"][c.category.name]["is_common"] = c.is_common
                subs = cat["subcategories"][c.category.name]["subcategories"]
                subs["is_common"] = c.is_common
                subs[c.name] += 1
            char_stats["Commons"][str(c.is_common)] += 1
            if c.characteristic_type:
                char_stats["Types"][c.characteristic_type.name] += 1

        # Convert sets to lists
        chars["characteristics"] = list(chars["characteristics"])
        chars["categories"] = list(chars["categories"])
        # Pattern
        pattern = {"category": "", "subcategory": None}
        if hasattr(b.category, "category"):
            pattern["category"] = b.category.category.name
            pattern["subcategory"] = b.category.name
        else:
            pattern["category"] = b.category.name
            pattern["subcategory"] = None

        # result
        res[bug_id] = {
            "language": b.language,
            "compiler": b.compiler,
            "is_correct": b.test_case_correct,
            "symptom": b.symptom.name,
            "pattern": pattern,
            "root_cause": {"category": b.root_cause.category.name,
                           "subcategory": b.root_cause.name},
            "chars": chars
        }
    with open(args.output, 'w') as f:
        json.dump(res, f, indent=4)
    with open(args.characteristics, 'w') as f:
        json.dump(char_stats, f, indent=4)
