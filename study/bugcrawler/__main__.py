import argparse

from bugcrawl import BugCrawl


COMMANDS = ['create']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command',
                        help="Command to execute: create",
                        default='get')
    parser.add_argument('lang',
                        help="lang to use: java, scala, kotlin, groovy all",
                        default='all')
    parser.add_argument('output',
                        help="Print output to this file",
                        default=None)
    parser.add_argument('before',
                        help="Find bugs before this date: YYYY-MM-DD",
                        default=None)
    parser.add_argument('after',
                        help="Find bugs after this date: YYYY-MM-DD",
                        default=None)
    args = parser.parse_args()

    if args.command not in COMMANDS:
        print("Invalid command")
        exit(1)

    filters = {
        'before': args.before,
        'after': args.after
    }
    bugcrawl = BugCrawl(lang=args.lang, filters=filters, output=args.output)
    getattr(bugcrawl, args.command)()


if __name__ == "__main__":
    main()
