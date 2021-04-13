#! /usr/bin/env python3
import argparse
import json

import kotlin as kt
import java as jv
import scala as sc
import groovy as gv


def get_args():
    parser = argparse.ArgumentParser(
        description='Serialize bugs.')
    parser.add_argument("output", help="File to save the bugs.")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    bugs = jv.java_iter1 + jv.java_iter2 + jv.java_iter3 + jv.java_iter4 + \
        sc.scala_iter1 + sc.scala_iter2 + sc.scala_iter3 + sc.scala_iter4 + \
        kt.kotlin_iter1 + kt.kotlin_iter2 + kt.kotlin_iter3 + kt.kotlin_iter4 + \
        gv.groovy_iter1 + gv.groovy_iter2 + gv.groovy_iter3 + gv.groovy_iter4
    res = {}
    for b in bugs:
        # symptoms

        # characteristics
        chars = {"characteristics": set(), "categories": set()}
        for c in b.characteristics:
            chars["characteristics"].add(c.name)
            if c.category is not None:
                chars["categories"].add(c.category.name)
        # Convert sets to lists
        chars["characteristics"] = list(chars["characteristics"])
        chars["categories"] = list(chars["categories"])
        # Category
        category = {"category": "", "subcategory": None}
        if hasattr(b.category, "category"):
            category["category"] = b.category.category.name
            category["subcategory"] = b.category.name
        else:
            category["category"] = b.category.name
            category["subcategory"] = None

        # result
        res[b.bug_id] = {
            "language": b.language,
            "compiler": b.compiler,
            "is_correct": b.test_case_correct,
            "symptom": b.symptom.name,
            "category": category,
            "root_cause": {"category": b.root_cause.category.name,
                           "subcategory": b.root_cause.name},
            "chars": chars
        }
    with open(args.output, 'w') as f:
        json.dump(res, f, indent=4)
