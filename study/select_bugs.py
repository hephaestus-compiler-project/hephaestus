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


def get_groovy_query():
    return {
        'lang': 'groovy',
        'type': 'bug',
        'status': 'closed',
        'resolution': 'fixed',
        '$or': [
            {'components': 'static type checker'},
            {'compomenets': 'static compilation'},
            {'compomenets': 'compiler'},
        ]
    }


def get_scala_query():
    return {
        'lang': 'scala',
        'status': 'closed',
        '$or': [
            {
                '$and': [
                    {
                        '$or': [
                            {'labels': 'bug'},
                            {'labels': 'itype:bug'},
                            {'labels': 'itype:crash'},
                        ]
                    },
                    {
                        '$or': [
                            {'labels': 'area:implicits'},
                            {'labels': 'area:gadt'},
                            {'labels': 'area:match-types'},
                            {'labels': 'area:nullability'},
                            {'labels': 'area:overloading'},
                            {'labels': 'area:pattern-matching'},
                            {'labels': 'area:typer'},
                            {'labels': 'area:erasure'},
                            {'labels': 'area:erased-terms'},
                        ]
                    }
                ]

            },
            {
                '$or': [
                    {'labels': 'blocker'},
                    {'labels': 'compiler crash'},
                    {'labels': 'dependent types'},
                    {'labels': 'erasure'},
                    {'labels': 'errors and warnings'},
                    {'labels': 'existential'},
                    {'labels': 'structural types'},
                    {'labels': 'gadt'},
                    {'labels': 'implicit classes'},
                    {'labels': 'implicit'},
                    {'labels': 'infer'},
                    {'labels': 'typer'},
                    {'labels': 'overloading'},
                    {'labels': 'patmat'},
                    {'labels': 'should compile'},
                    {'labels': 'should not compile'},
                    {'labels': 'runtime crash'},
                    {'labels': 'singleton-type'},
                    {'labels': 'typelevel'},
                ]
            }
        ],
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
