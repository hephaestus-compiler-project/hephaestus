import json
import inspect
from collections import defaultdict
import symptoms
from characteristics import CharacteristicCategory, Characteristic


def print_characteristics():
    def get_name(characteristic):
        if isinstance(characteristic(), Characteristic):
            sub_categories = [
                get_name(s) for s in Characteristic.__subclasses__()
                if s.category.__class__ == characteristic
            ]
            if len(sub_categories) > 0:
                return characteristic.name + \
                    " -- " + characteristic.characteristic_type.name + \
                    " (" + ", ".join(sub_categories) + ")"
        if getattr(characteristic, "characteristic_type", None):
            return characteristic.name + " -- " + characteristic.characteristic_type.name
        return characteristic.name
    print("======Characteristics======")
    chars = {
        g.name: [get_name(s) for s in Characteristic.__subclasses__()
        if s.category.__class__ == g]
        for g in CharacteristicCategory.__subclasses__()
    }
    for g, s in chars.items():
        print(g)
        if s:
            print("\t" + "\n\t".join(s))
    print("===========================")


def print_stats(bugs):
    #  print("======Statistics======")
    stats = {
        "Bugs": defaultdict(lambda: 0),
        "Characteristics": {
            "Categories": defaultdict(
                lambda: {"total": 0,
                         "subcategories": defaultdict(lambda: {"total": 0,
                                                      "subcategories": defaultdict(
                                                          lambda: 0)})}),
            "Types": defaultdict(lambda: 0),
            "Commons": {"True": 0, "False": 0}},
        "Correctness": {"Correct": 0, "Incorrect": 0},
        "Symptoms": defaultdict(lambda: 0),
        "Categories": defaultdict(lambda: 0),
        "Root Causes": defaultdict(
            lambda: {"Subcategories": defaultdict(lambda: 0),
                     "total": 0})
    }
    for b in bugs:
        stats['Bugs'][b.language] += 1
        visited = set()
        for c in b.characteristics:
            if isinstance(c.category, CharacteristicCategory):
                cat = stats["Characteristics"]["Categories"][c.category.name]
                if c.category.name not in visited:
                    cat["total"] += 1
                    visited.add(c.category.name)
                cat["subcategories"][c.name]["total"] += 1
                cat["subcategories"][c.name]["is_common"] = c.is_common
            else:
                cat = stats["Characteristics"]["Categories"][c.category.category.name]
                if c.category.category.name not in visited:
                    cat["total"] += 1
                    visited.add(c.category.category.name)
                cat["subcategories"][c.category.name]["total"] += 1
                cat["subcategories"][c.category.name]["is_common"] = c.is_common
                subs = cat["subcategories"][c.category.name]["subcategories"]
                subs["is_common"] = c.is_common
                subs[c.name] += 1
            stats["Characteristics"]["Commons"][str(c.is_common)] += 1
            if c.characteristic_type:
                stats["Characteristics"]["Types"][c.characteristic_type.name] += 1
        if b.test_case_correct:
            stats["Correctness"]["Correct"] += 1
        else:
            stats["Correctness"]["Incorrect"] += 1
        stats["Symptoms"][b.symptom.name] += 1
        stats["Categories"][b.category.name] += 1
        root_cause = stats["Root Causes"][b.root_cause.name]
        root_cause["total"] += 1
    print(json.dumps(stats, indent=4))
    print("======================")
    return stats


def print_symptoms():
    def print_s(name, doc, symbol="-"):
        l = len(name)
        print(name)
        print(l * symbol)
        print(doc)

    syms = [obj for name, obj in inspect.getmembers(symptoms) if inspect.isclass(obj)]
    top_level = {tp: [] for tp in syms if not any(s for s in tp.mro() if s in syms and s != tp)}
    for s in syms:
        tp = [i for i in s.mro() if i in syms and i != s]
        if len(tp) == 1:
            top_level[tp[0]].append(s)
        elif len(tp) > 1:
            raise
    for tp, syms in top_level.items():
        print_s(tp.__name__, tp.__doc__, "=")
        for s in syms:
            name = s.__name__ + " (" + tp.__name__ + ")"
            print_s(name, s.__doc__)


from kotlin import *
from java import *
from scala import *
from groovy import *


stats = print_stats(
    java_iter1 + java_iter2 + java_iter3 + java_iter4 + \
    scala_iter1 + scala_iter2 + scala_iter3 + scala_iter4 + \
    kotlin_iter1 + kotlin_iter2 + kotlin_iter3 + kotlin_iter4 + \
    groovy_iter1 + groovy_iter2 + groovy_iter3 + groovy_iter4)
