"""Fetch kotlin bugs.
oracle, mutator, resolution, status, symptom must be completed manually
"""
import argparse
import requests
import os
import json
import re
from datetime import datetime
from copy import deepcopy


COMPILER = "kotlinc"
LANGUAGE = "Kotlin"
SCHEMA = {
    "date": "",
    "language": LANGUAGE,
    "compiler": COMPILER,
    "version": "",
    "bugid": "",
    "title": "",
    "links": {
        "issuetracker": "",
        "fix": ""
    },
    "oracle": "",
    "mutator": "",
    "severity": "",
    "reporter": "",
    "status": "",
    "resolution": "",
    "resolutiondate": "",
    "symptom": "",
    "bugtype": "",
    "resolvedin": "",
    "test": [],
    "chars": {
        "characteristics": []
    },
    "errormsg": [],
    "comment": ""
}


def get_code_fragments(text):
    matches = re.findall('(?:```)(.*?)(?:```)', text, flags=re.I | re.DOTALL)
    res = []
    for m in matches:
        res.append([x.replace('\t', '  ') for x in m.splitlines()
                    if x.strip() not in ('', 'kotlin')])
        res = [r for r in res if len(r) > 0]
    return res


def get_data(lookup):
    skip = 0
    top = 2500
    results = []

    # we don't need to loop (< 2500 bugs)
    base = "https://youtrack.jetbrains.com/api/issues"
    search_terms = [
        "project: Kotlin",
        "Reporter: theosotr, stefanoshaliassos"
    ]
    query = "%20".join(map(lambda x: x.replace(" ", "%20"), search_terms))
    fields = "idReadable,description,created,reporter(login),resolved,"
    fields += "summary,fields(value(login))"
    url = "{base}?query={query}&fields={fields}&$skip={skip}&$top={top}"
    url = url.format(
        base=base,
        query=query,
        fields=fields,
        skip=skip,
        top=top
    )
    response = requests.get(url)
    youtrack_url = "https://youtrack.jetbrains.com/issue/"
    for item in response.json():
        created = datetime.utcfromtimestamp(int(item['created']) / 1000.0)
        try:
            resolution = datetime.utcfromtimestamp(
                int(item['resolved']) / 1000.0)
        except:
            resolution = None
        passed = resolution - created if resolution else None
        reporter = item['reporter']['login']

        bid = item['idReadable']
        if bid in lookup:
            bug = lookup[bid]
        else:
            bug = deepcopy(SCHEMA)
        bug['date'] = str(created)
        bug['resolutiondate'] = str(resolution)
        bug['resolvedin'] = str(passed)
        bug['bugid'] = bid
        bug['title'] = item['summary']
        bug['links']['issuetracker'] = youtrack_url + bid
        bug['reporter'] = reporter
        if bug.get('chars', None) is None:
            bug['chars'] = SCHEMA['chars']

        description = item['description']
        description = description if description is not None else ""
        code_fragments = get_code_fragments(description)
        if len(code_fragments) >= 1:
            if not len(lookup.get(bug['bugid'], {}).get('test', [])) >= 1:
                bug['test'] = code_fragments[0]
        if len(code_fragments) >= 2:
            if not len(lookup.get(bug['bugid'], {}).get('errormsg', [])) >= 1:
                bug['errormsg'] = code_fragments[1]
        if len(code_fragments) != 2:
            print("{}: code fragments {}".format(
                bug['bugid'], len(code_fragments)
            ))
        results.append(bug)
    # Add bugs in lookup but not in current set (e.g. from another tracker)
    ids = {bug['bugid'] for bug in results}
    for bug_id, bug in lookup.items():
        if bug_id not in ids:
            if bug.get('chars', None) is None:
                bug['chars'] = SCHEMA['chars']
            results.append(bug)
    return results


def get_args():
    parser = argparse.ArgumentParser(
        description='Fetch kotlin front-end bugs.')
    parser.add_argument("output", help="File to save the bugs.")
    return parser.parse_args()

def main():
    args = get_args()
    lookup = {}
    if os.path.isfile(args.output):
        with open(args.output) as f:
            tmp = json.load(f)
            for bug in tmp:
                lookup[bug['bugid']] = bug
    data = get_data(lookup)
    with open(args.output, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    main()
