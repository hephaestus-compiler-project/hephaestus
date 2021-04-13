#! /usr/bin/env python3
import argparse
import json

import matplotlib.pylab as plt
import matplotlib.offsetbox as offsetbox
import seaborn as sns
import pandas as pd


def get_args():
    parser = argparse.ArgumentParser(
        description='Generate characteristics figure.')
    parser.add_argument("data", help="JSON with bugs.")
    parser.add_argument(
            "--output",
            default="characteristics.pdf",
            help="Filename to save the figure.")
    return parser.parse_args()


def construct_dataframe(data):
    characteristics = []
    dataframes = {}
    for key, value in data.items():
        framedata = []
        for subkey, subvalue in value['subcategories'].items():
            framedata.append({
                'Characteristic': subkey,
                'Number of bugs': 100 * (int(subvalue['total']) / 320),
            })
            if 'is_common' not in subvalue:
                print(subkey)
            if subvalue['is_common']:
                characteristics.append((subkey, subvalue['is_common'],
                                        100 * (int(subvalue['total']) / 320)))
        framedata = sorted(framedata, key=lambda k: k['Number of bugs'],
                           reverse=True)[:4]
        percentage = str(round((int(value['total']) / 320) * 100, 2))
        dataframes[key + " (" + percentage + "%)"] = pd.DataFrame(framedata)
    return dataframes, characteristics


def plot_fig(dataframes, output):
    plt.style.use('ggplot')
    sns.set(style="whitegrid")
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['figure.figsize'] = (8, 4.5)
    plt.rcParams['axes.labelsize'] = 8
    plt.rcParams['ytick.labelsize'] = 6.8
    plt.rcParams['xtick.labelsize'] = 6
    plt.rcParams['font.serif'] = 'DejaVu Sans'
    plt.rcParams['font.monospace'] = 'Inconsolata Medium'
    plt.rcParams['axes.labelweight'] = 'bold'

    fig, axs = plt.subplots(nrows=8, sharex=True)

    for i, (key, dataframe) in enumerate(dataframes.items()):
        dataframe = dataframe.sort_values(
            'Number of bugs', ascending=True)
        dataframe.plot.barh(x='Characteristic', y='Number of bugs',
                            color='grey', ax=axs[i])
        ob = offsetbox.AnchoredText(key, loc=1,
                                    prop=dict(color='black', fontsize=7))
        ob.patch.set(boxstyle='round', color='lightgrey', alpha=1)
        axs[i].add_artist(ob)
        axs[i].set_ylabel('')
        axs[i].set_xlabel('Number of bugs (%)')
        axs[i].get_legend().remove()
        axs[i].set_xlim([0, 70])
        for line in axs[i].get_xgridlines():
            line.set_linewidth(0.3)
        for line in axs[i].get_ygridlines():
            line.set_linewidth(0.3)
        [i.set_linewidth(0.3) for i in axs[i].spines.values()]
    plt.savefig(output, format='pdf', bbox_inches='tight',
                pad_inches=0)


def main():
    args = get_args()
    with open(args.data, 'r') as f:
        json_data = json.load(f)
    dataframes, characteristics = construct_dataframe(json_data['Categories'])
    characteristics = sorted(characteristics, key=lambda tup: tup[2])
    print(characteristics[:7])
    print(characteristics[-7:])
    plot_fig(dataframes, args.output)


if __name__ == "__main__":
    main()
