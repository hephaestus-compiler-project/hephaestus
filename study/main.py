import argparse

from bugcrawler.bugcrawl import BugCrawler


COMMANDS = ['get']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--command',
                        '-c',
                        help="Command to execute: get",
                        default='get')
    parser.add_argument('--lang',
                        '-l',
                        help="Engine to use: java, scala, kotlin, groovy, all",
                        default='all')
    parser.add_argument('--output',
                        '-o',
                        help="Print output to this file",
                        default=None)
    parser.add_argument('--db',
                        help="Name of database",
                        default='test')
    parser.add_argument('--collection',
                        help="Name of collection",
                        default='jsbugs')
    args = parser.parse_args()

    if args.command not in COMMANDS:
        print("Invalid command")
        exit(1)

    filters = {
    }
    bugcrawler = BugCrawler(lang=args.lang, filters=filters,
                            output=args.output)
    getattr(bugcrawler, args.command)()


if __name__ == "__main__":
    main()
