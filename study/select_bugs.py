import argparse

import pymongo


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['bugdb']
col = db['bug']


def get_kotlin_query():
    return {
        'lang': 'kotlin',
        '$or': [
            {'components': "frontend"},
            {'components': "frontend. control-flow analysis"},
            {'components': "frontend. data-flow analysis"},
            {'components': "frontend. declarations"},
            {'components': "frontend. ir"},
            {'components': "frontend. resolution and inference"},
        ]
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang',
                        '-l',
                        required=True,
                        help="Language to use: java, scala, kotlin, groovy")
    parser.add_argument('--output',
                        '-o',
                        required=True,
                        help="Print output to this file")
    args = parser.parse_args()

    fun = globals()['get_' + args.lang + "_query"]
    bugs = [e['url'] for e in col.find(fun())]
    with open(args.output, 'w') as out:
        out.write('\n'.join(bugs))


if __name__ == "__main__":
    main()
