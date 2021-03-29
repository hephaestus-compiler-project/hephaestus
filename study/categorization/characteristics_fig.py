#! /usr/bin/env python3
import matplotlib.pylab as plt
import matplotlib.offsetbox as offsetbox
import seaborn as sns
import pandas as pd

from utils import stats


def construct_dataframe(data):
    dataframes = {}
    for key, value in data.items():
        framedata = []
        for subkey, subvalue in value['subcategories'].items():
            framedata.append({
                'Characteristic': subkey,
                'Number of bugs': 100 * (int(subvalue['total']) / 240),
            })
        framedata = sorted(framedata, key=lambda k: k['Number of bugs'],
                           reverse=True)[:4]
        percentage = str(round((int(value['total']) / 240) * 100, 2))
        dataframes[key + " (" + percentage + "%)"] = pd.DataFrame(framedata)
    return dataframes


plt.style.use('ggplot')
sns.set(style="whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.figsize'] = (6.5, 4)
plt.rcParams['axes.labelsize'] = 6
plt.rcParams['ytick.labelsize'] = 4.5
plt.rcParams['xtick.labelsize'] = 6
plt.rcParams['font.serif'] = 'DejaVu Sans'
plt.rcParams['font.monospace'] = 'Inconsolata Medium'
plt.rcParams['axes.labelweight'] = 'bold'

fig, axs = plt.subplots(nrows=8, sharex=True)
dataframes = construct_dataframe(
    stats['Characteristics']['Categories'])

for i, (key, dataframe) in enumerate(dataframes.items()):
    dataframe = dataframe.sort_values(
        'Number of bugs', ascending=True)
    dataframe.plot.barh(x='Characteristic', y='Number of bugs',
                        color='grey', ax=axs[i])
    ob = offsetbox.AnchoredText(key, loc=1,
                                prop=dict(color='black', fontsize=4))
    ob.patch.set(boxstyle='round', color='lightgrey', alpha=1)
    axs[i].add_artist(ob)
    axs[i].set_ylabel('')
    axs[i].set_xlabel('Number of bugs (%)')
    axs[i].get_legend().remove()
    axs[i].set_xlim([0, 60])
    for line in axs[i].get_xgridlines():
        line.set_linewidth(0.3)
    for line in axs[i].get_ygridlines():
        line.set_linewidth(0.3)
    [i.set_linewidth(0.3) for i in axs[i].spines.values()]
plt.savefig("characteristics.pdf", format='pdf', bbox_inches='tight',
            pad_inches=0)
