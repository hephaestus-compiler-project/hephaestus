#! /usr/bin/env python3
from collections import defaultdict

import matplotlib.pylab as plt
import seaborn as sns
import pandas as pd

import categories as ct
from utils import stats


def map_category_name(category_name):
    if category_name in [
            ct.Approximation().name,
            ct.Inference().name,
            ct.TypeComparison().name]:
        return "Type-related Bugs"
    elif category_name in [
            ct.OtherSemanticChecking().name,
            ct.TypeExpression().name,
            ct.Declarations().name]:
        return "Semantic Checking Bugs"
    elif category_name in [
            ct.Resolution().name,
            ct.Environment().name]:
        return "Resolution Bugs"
    else:
        return category_name


def construct_dataframe(data):
    new_data = defaultdict(lambda: 0)
    for key, value in data.items():
        new_key = map_category_name(key)
        new_data[new_key] += int(value)

    framedata = []
    for key, value in new_data.items():
        framedata.append({
            'Type': key,
            'Number of bugs': int(value),
        })
    return pd.DataFrame(framedata)


plt.style.use('ggplot')
sns.set(style="whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.figsize'] = (8, 4)
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['font.serif'] = 'DejaVu Sans'
plt.rcParams['font.monospace'] = 'Inconsolata Medium'
plt.rcParams['axes.labelweight'] = 'bold'

dataframe = construct_dataframe(stats['Categories']).sort_values(
    'Number of bugs', ascending=True)
ax = dataframe.plot.barh(width=0.3, x='Type', color='grey')
for p in ax.patches:
    ax.annotate("{} / 160".format(p.get_width()),
                (p.get_x() + p.get_width(), p.get_y()),
                xytext=(5, 10), textcoords='offset points')
ax.set_ylabel('')
patches, labels = ax.get_legend_handles_labels()
ax.legend(patches, ('Number of bugs',), loc='lower right')
plt.savefig("patterns.pdf", format='pdf', bbox_inches='tight',
            pad_inches=0)
