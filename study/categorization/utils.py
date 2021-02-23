import json
from collections import defaultdict
from characteristics import CharacteristicCategory

def print_characteristics():
    def get_name(characteristic):
        if characteristic.is_category:
            sub_categories = [
                s.name for s in SpecificCharacteristic.__subclasses__()
                if s.specific_category == characteristic
            ]
            return characteristic.name + "(" + ", ".join(sub_categories) + ")"
        return characteristic.name
    print("======Characteristic======")
    chars = {
        g.name: [get_name(s) for s in SpecificCharacteristic.__subclasses__() 
        if s.general_characteristic == g] 
        for g in GeneralCharacteristic.__subclasses__()
    }
    for g, s in chars.items():
        print(g)
        if s:
            print("\t" + "\n\t".join(s))
    print("==========================")

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
