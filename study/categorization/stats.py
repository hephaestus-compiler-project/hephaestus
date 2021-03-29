import json
from collections import defaultdict
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
for bug in bugs:
    assert "." in bug.bug_id
    bid = bug.bug_id.split(".")[-1].replace("Dotty", "dotty").replace(
        "Scala2", "scala")
    root_causes[bug.root_cause.category.name].append(bid)
with open('root_causes.json', 'w') as fp:
    json.dump(root_causes, fp)
