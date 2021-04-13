#! /usr/bin/env python3
import argparse
import json

from collections import defaultdict

import matplotlib.pylab as plt
import seaborn as sns
import pandas as pd


def get_args():
    parser = argparse.ArgumentParser(
        description='Generate patterns figure.')
    parser.add_argument("data", help="JSON with bugs.")
    parser.add_argument(
            "--output",
            default="patterns.pdf",
            help="Filename to save the figure.")
    return parser.parse_args()


def construct_dataframe(bugs):
    data = defaultdict(lambda: 0)
    for bug in bugs.values():
        data[(bug['language'], bug['pattern']['category'])] += 1
    framedata = []
    for (lang, category), value in data.items():
        framedata.append({
            "Pattern": category,
            "Language": lang,
            "Number of bugs": value
        })
    return pd.DataFrame(framedata), data


def plot_fig(df, data, categories, output):
    plt.style.use('ggplot')
    sns.set(style="whitegrid")
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['figure.figsize'] = (9, 2.5)
    plt.rcParams['axes.labelsize'] = 17
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['font.serif'] = 'DejaVu Sans'
    plt.rcParams['font.monospace'] = 'Inconsolata Medium'
    plt.rcParams['axes.labelweight'] = 'bold'
    ax = df.plot.barh(width=0.3,
                      color=['#e69f56', '#b07219', '#f18e33', '#c22d40'],
                      stacked=True)

    sums = []
    for c in categories:
        v = sum(data[(lang, c)]
                for lang in ['Groovy', 'Java', 'Kotlin', 'Scala'])
        sums.append(v)

    for i, p in enumerate(ax.patches[15:]):
        ax.annotate("{} / 320".format(int(sums[i])),
                    (p.get_x() + p.get_width(), p.get_y()),
                    xytext=(5, 10), textcoords='offset points')
    ax.set_ylabel('')
    patches, labels = ax.get_legend_handles_labels()
    plt.savefig(output, format='pdf', bbox_inches='tight',
                pad_inches=0)


def main():
    args = get_args()
    with open(args.data, 'r') as f:
        json_data = json.load(f)
    df, data = construct_dataframe(json_data)
    df = df.groupby(['Language', 'Pattern'])['Number of bugs'].sum().unstack(
        'Language')
    categories = [
        'AST Transformation Bugs',
        'Error Handling & Reporting Bugs',
        'Resolution & Environment Bugs',
        'Semantic Analysis Bugs',
        'Type-related Bugs',
    ]
    df = df.reindex(categories)
    print(df)
    plot_fig(df, data, categories, args.output)



if __name__ == "__main__":
    main()
