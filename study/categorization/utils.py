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
    print("======Statistics======")
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
        "Root Causes": defaultdict(lambda: 0),
        "Categories": defaultdict(lambda: 0)
    }
    for b in bugs:
        stats['Bugs'][b.language] += 1
        for c in b.characteristics:
            if isinstance(c.category, CharacteristicCategory):
                cat = stats["Characteristics"]["Categories"][c.category.name]
                cat["total"] += 1
                cat["subcategories"][c.name]["total"] += 1
            else:
                cat = stats["Characteristics"]["Categories"][c.category.category.name]
                cat["total"] += 1
                cat["subcategories"][c.category.name]["total"] += 1
                subs = cat["subcategories"][c.category.name]["subcategories"]
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
        stats["Root Causes"][b.root_cause.name] += 1
    print(json.dumps(stats, indent=4))
    print("======================")


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
print_symptoms()
