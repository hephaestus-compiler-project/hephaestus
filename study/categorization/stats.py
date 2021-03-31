import json
from collections import defaultdict
from characteristics import CharacteristicCategory
from kotlin import *
from java import *
from scala import *
from groovy import *
from kotlin import kotlin_iter1
from utils import print_stats, print_characteristics

#print_stats(kotlin_iter1)
#print_characteristics()


bugs = java_iter1 + java_iter2 + java_iter3 + \
    scala_iter1 + scala_iter2 + scala_iter3 + \
    kotlin_iter1 + kotlin_iter2 + kotlin_iter3 + \
    groovy_iter1 + groovy_iter2 + groovy_iter3


root_causes = defaultdict(lambda: [])
symptoms = defaultdict(lambda: [])
categories = defaultdict(lambda: [])
characteristics = defaultdict(lambda: {"characteristics": [],
                                       "categories": set()})
for bug in bugs:
    assert "." in bug.bug_id
    bid = bug.bug_id.split(".")[-1].replace("Dotty", "dotty").replace(
        "Scala2", "scala")
    root_causes[bid].append(bug.root_cause.category.name)
    categories[bid].append(bug.category.name)
    symptoms[bid].append(bug.symptom.name)
    for char in bug.characteristics:
        if not isinstance(char, CharacteristicCategory):
            characteristics[bid]["characteristics"].append(char.name)
            if char.category is not None:
                characteristics[bid]["categories"].add(
                    char.category.name)
        else:
            characteristics[bid]["categories"].add(char.name)
    characteristics[bid]["categories"] = list(
        characteristics[bid]["categories"])
with open('root_causes.json', 'w') as fp:
    json.dump(root_causes, fp)


for bug in bugs:
    assert "." in bug.bug_id
    bid = bug.bug_id.split(".")[-1].replace("Dotty", "dotty").replace(
        "Scala2", "scala")
    root_causes[bid].append(bug.root_cause.category.name)
with open('root_causes.json', 'w') as fp:
    json.dump(root_causes, fp)
with open('characteristics.json', 'w') as fp:
    json.dump(characteristics, fp)
with open('categories.json', 'w') as fp:
    json.dump(categories, fp)
with open('symptoms.json', 'w') as fp:
    json.dump(symptoms, fp)
