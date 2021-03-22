#! /usr/bin/env python3
import matplotlib.pylab as plt
import seaborn as sns
import pandas as pd

from utils import stats


def construct_dataframe(data):
    framedata = []
    for key, value in data.items():
        total = value['total']
        framedata.append({
            'Root Cause': key,
            'Number of bugs': int(total),
        })
    return pd.DataFrame(framedata)


total_bugs = sum(v['total'] for v in stats['Root Causes'].values())

plt.style.use('ggplot')
sns.set(style="whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.figsize'] = (8, 4)
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['font.serif'] = 'DejaVu Sans'
plt.rcParams['font.monospace'] = 'Inconsolata Medium'
plt.rcParams['axes.labelweight'] = 'bold'

dataframe = construct_dataframe(stats['Root Causes']).sort_values(
    'Number of bugs', ascending=True)
ax = dataframe.plot.barh(width=0.3, x='Root Cause', color='grey')
for i, p in enumerate(ax.patches):
    ax.annotate("{} / {}".format(p.get_width(), total_bugs),
                (p.get_x() + p.get_width(), p.get_y()),
                xytext=(5, 10), textcoords='offset points')
    percentage = '{:.2f}%'.format(100 * p.get_width()/total_bugs)
    if p.get_width() < 15:
        x = p.get_x() + 0.5
    else:
        x = p.get_x() + p.get_width() / 2 - 0.3
    y = p.get_y() + p.get_height() / 2 - 0.06
    ax.annotate(percentage, (x, y), fontsize="xx-small")
ax.set_ylabel('')
patches, labels = ax.get_legend_handles_labels()
ax.legend(patches, ('Number of bugs',), loc='lower right')
plt.savefig("root_causes.pdf", format='pdf', bbox_inches='tight',
            pad_inches=0)
