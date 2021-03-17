#! /usr/bin/env python3
import matplotlib.pylab as plt
import seaborn as sns
import pandas as pd

from utils import stats


def construct_dataframe(data):
    framedata = []
    for key, value in data.items():
        framedata.append({
            'Symptom': key,
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

dataframe = construct_dataframe(stats['Symptoms']).sort_values(
    'Number of bugs', ascending=True)
ax = dataframe.plot.barh(width=0.3, x='Symptom', color='grey')
for p in ax.patches:
    ax.annotate("{} / 160".format(p.get_width()),
                (p.get_x() + p.get_width(), p.get_y()),
                xytext=(5, 10), textcoords='offset points')
ax.set_ylabel('')
patches, labels = ax.get_legend_handles_labels()
ax.legend(patches, ('Number of bugs',), loc='lower right')
plt.savefig("symptoms.pdf", format='pdf', bbox_inches='tight',
            pad_inches=0)
