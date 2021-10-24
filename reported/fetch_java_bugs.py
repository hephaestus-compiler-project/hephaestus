"""Fetch java bugs.
"""
import argparse
import requests
import os
import json
import re
from datetime import datetime
from copy import deepcopy

BUGS = [
    "JDK-8267220",
    "JDK-8267610",
    "JDK-8268159",
    "JDK-8269348",
    "JDK-8269386",
    "JDK-8269586",
    "JDK-8269737",
    "JDK-8269738",
    "JDK-8272077",
    "JDK-8274183"
]
COMPILER = "javac"
LANGUAGE = "Java"
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
    matches = re.findall('(?:---------- BEGIN SOURCE ----------)(.*?)(?:---------- END SOURCE ----------)', text, flags=re.I | re.DOTALL)
    res = []
    for m in matches:
        res.append([x.replace('\t', '  ') for x in m.splitlines() if x.strip() != ''])
        res = [r for r in res if len(r) > 0]
    return res

def get_data(lookup):
    start_at = 0
    max_results = 1000
    results = []
    # No need for loop, less than 1000
    base = "https://bugs.openjdk.java.net/rest/api/latest/search"
    search_terms = [
        "project = JDK",
        "AND id in ({})".format(", ".join(BUGS)),
    ]
    query = "%20".join(map(lambda x: x.replace(" ", "%20"), search_terms))
    fields = "key,description,resolutiondate,created,reporter,summary,status,resolution"
    url = "{base}?jql={query}&fields={fields}&startAt={s}&maxResults={m}"
    url = url.format(
        base=base,
        query=query,
        fields=fields,
        s=start_at,
        m=max_results
    )
    response = requests.get(url).json()
    openjdk_url = "https://bugs.openjdk.java.net/browse/"
    for item in response['issues']:
        created = datetime.strptime(
            item['fields']['created'], "%Y-%m-%dT%H:%M:%S.%f%z")
        passed = None
        try:
            resolution = datetime.strptime(
                item['fields']['resolutiondate'], "%Y-%m-%dT%H:%M:%S.%f%z")
            passed = resolution - created
        except:
            resolution = None
        reporter = item['fields']['reporter']['name']
        bugid = item['key']
        if bugid in lookup:
            bug = lookup[bugid]
        else:
            bug = deepcopy(SCHEMA)

        bug['date'] = str(created)
        bug['resolutiondate'] = str(resolution)
        bug['resolvedin'] = str(passed)
        bug['bugid'] = bugid
        bug['title'] = item['fields']['summary']
        bug['links']['issuetracker'] = openjdk_url + bugid
        bug['reporter'] = reporter
        if item['fields']['resolution']:
            bug['resolution'] = str(item['fields']['resolution']['name'])
        bug['status'] = str(item['fields']['status']['name'])
        if bug.get('chars', None) is None:
            bug['chars'] = SCHEMA['chars']

        description = item['fields']['description']
        code_fragments = get_code_fragments(description)
        if len(code_fragments) >= 1:
            if not len(lookup.get(bug['bugid'], {}).get('test', [])) >= 1:
                bug['test'] = code_fragments[0]
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
        description='Fetch Java bugs.')
    parser.add_argument("input", help="File to save read and save bugs.")
    return parser.parse_args()

def main():
    args = get_args()
    lookup = {}
    if os.path.isfile(args.input):
        with open(args.input) as f:
            tmp = json.load(f)
            for bug in tmp:
                lookup[bug['bugid']] = bug
    data = get_data(lookup)
    with open(args.input, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    main()
