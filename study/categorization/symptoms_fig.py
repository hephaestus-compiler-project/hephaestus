#! /usr/bin/env python3
from collections import defaultdict

import matplotlib.pylab as plt
import seaborn as sns
import pandas as pd

import kotlin as kt
import java as jv
import scala as sc
import groovy as gv


def construct_dataframe(bugs):

    data = defaultdict(lambda: 0)
    for bug in bugs:
        data[(bug.language, bug.symptom.name)] += 1
    framedata = []
    for (lang, symptom), value in data.items():
        framedata.append({
            "Symptom": symptom,
            "Language": lang,
            "Number of bugs": value
        })
    return pd.DataFrame(framedata), data


plt.style.use('ggplot')
sns.set(style="whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.figsize'] = (8, 4)
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['font.serif'] = 'DejaVu Sans'
plt.rcParams['font.monospace'] = 'Inconsolata Medium'
plt.rcParams['axes.labelweight'] = 'bold'

bugs = jv.java_iter1 + jv.java_iter2 + jv.java_iter3 + \
    sc.scala_iter1 + sc.scala_iter2 + sc.scala_iter3 + \
    kt.kotlin_iter1 + kt.kotlin_iter2 + kt.kotlin_iter3 + \
    gv.groovy_iter1 + gv.groovy_iter2 + gv.groovy_iter3

df, data = construct_dataframe(bugs)
df = df.groupby(['Language', 'Symptom'])['Number of bugs'].sum().unstack('Language')
categories = [
    'Compilation Performance Issue',
    'Misleading Report',
    'Unexpected Runtime Behavior',
    'Internal Compiler Error',
    'Unexpected Compile-Time Error',
]
df = df.reindex(categories)

ax = df.plot.barh(width=0.3, color=['#f6cb7d', '#873e23', '#e28743', '#8A0528'],
                  stacked=True)

sums = []
for c in categories:
    v = sum(data[(lang, c)] for lang in ['Groovy', 'Java', 'Kotlin', 'Scala'])
    sums.append(v)

for i, p in enumerate(ax.patches[15:]):
    ax.annotate("{} / 240".format(int(sums[i])),
                (p.get_x() + p.get_width(), p.get_y()),
                xytext=(5, 10), textcoords='offset points')
ax.set_ylabel('')
patches, labels = ax.get_legend_handles_labels()
plt.savefig("symptoms.pdf", format='pdf', bbox_inches='tight',
            pad_inches=0)
