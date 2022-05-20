"""Fetch groovy bugs.
oracle, mutator, symptom must be completed manually
"""
import argparse
import requests
import os
import json
import re
from copy import deepcopy
from datetime import datetime


COMPILER = "groovyc"
LANGUAGE = "Groovy"
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
    matches = re.findall('(?:{code:?(?:java|groovy)?})(.*?)(?:{code})', text, flags=re.I | re.DOTALL)
    res = []
    for m in matches[:1]:
        res.append([x.replace('\t', '  ') for x in m.splitlines() if x.strip() != ''])
        res = [r for r in res if len(r) > 0]
    return res


def get_data(lookup):
    start_at = 0
    max_results = 50
    total = 0
    results = []
    first = True
    while start_at < total or first:
        first = False
        base = "https://issues.apache.org/jira/rest/api/latest/search"
        search_terms = [
            'project = Groovy',
            'AND type = bug',
            'AND reporter = theosot OR reporter = schaliasos'
        ]
        query = "%20".join(map(lambda x: x.replace(" ", "%20"), search_terms))
        fields = "key,description,resolutiondate,created,reporter,resolution,status,summary"
        url = "{base}?jql={query}&fields={fields}&startAt={s}&maxResults={m}"
        url = url.format(
            base=base,
            query=query,
            fields=fields,
            s=start_at,
            m=max_results
        )
        print(url)
        response = requests.get(url).json()
        total = response['total']
        groovy_jira_url = "https://issues.apache.org/jira/browse/"
        for item in response['issues']:
            created = datetime.strptime(
                item['fields']['created'], "%Y-%m-%dT%H:%M:%S.%f%z")
            try:
                resolution = datetime.strptime(
                    item['fields']['resolutiondate'], "%Y-%m-%dT%H:%M:%S.%f%z")
            except:
                resolution = None
            passed = resolution - created if resolution else None
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
            bug['links']['issuetracker'] = groovy_jira_url + bugid
            bug['reporter'] = reporter
            if item['fields']['resolution']:
                bug['resolution'] = str(item['fields']['resolution']['name'])
            bug['status'] = str(item['fields']['status']['name'])

            description = item['fields']['description']
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
            if bug.get('chars', None) is None:
                bug['chars'] = SCHEMA['chars']
            results.append(bug)
        start_at += max_results
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
        description='Fetch groovy front-end bugs.')
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
