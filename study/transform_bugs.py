import argparse
import json
from datetime import datetime


def load_bugs(bug_file):
    with open(bug_file) as f:
        return json.load(f)


def save_bugs(bug_file, bugs):
    with open(bug_file, 'w') as f:
        f.write(json.dumps(bugs, indent=2))


def transform_groovy(bugs):
    new_bugs = []
    for bug in bugs:
        components = bug['data']['fields']['components'] or []
        versions = bug['data']['fields']['versions'] or []
        reporter = bug['data']['fields']['reporter'] or {}
        resolution = bug['data']['fields']['resolution'] or {}
        priority = bug['data']['fields']['priority'] or {}
        bug_dict = {
            'id': bug['data']['key'],
            'url': 'https://issues.apache.org/jira/browse/' + bug['data']['key'],
            'lang': 'groovy',
            'type': bug['data']['fields']['issuetype']['name'].lower(),
            'status': bug['data']['fields']['status']['name'].lower(),
            'resolution': resolution['name'].lower() if 'name' in resolution else None,
            'summary': bug['data']['fields']['summary'],
            'reporter': reporter.get('displayName'),
            'versions': [v['name'] for v in versions],
            'labels': bug['data']['fields']['labels'] or [],
            'components': [v['name'].lower() for v in components],
            'created': bug['data']['fields']['created'],
            'priority': priority.get('name')
        }
        new_bugs.append(bug_dict)
    return new_bugs


def transform_date(date):
    return datetime.utcfromtimestamp(date / 1000).strftime(
        '%Y-%m-%dT%H:%M:%SZ')


def transform_kotlin(bugs):
    new_bugs = []
    custom_fields = {
        'Priority': ('priority',
                     lambda x: x['name'].lower() if 'name' in x  else None),
        'Affected versions': ('versions', lambda x: [v['name'] for v in x]),
        'Subsystems': ('components', lambda x: [v['name'].lower() for v in x]),
    }
    for bug in bugs:
        bug_dict = {
            'id': bug['idReadable'],
            'url': 'https://youtrack.jetbrains.com/issue/' + bug['idReadable'],
            'lang': 'kotlin',
            'summary': bug['summary'],
            'type': 'bug',
            'status': 'closed',
            'reporter': None,
            'resolution': 'fixed',
            'labels': [],
            'created': transform_date(bug['created']),
        }
        for f in bug['customFields']:
            if f['name'] not in custom_fields:
                continue
            key, fun = custom_fields[f['name']]
            bug_dict[key] = fun(f['value'] or {})

        new_bugs.append(bug_dict)
    return new_bugs


def transform_scala2(bugs):
    new_bugs = []
    for bug in bugs:
        bug_id = bug['data']['html_url'].split('/')[-1]
        milestone = bug['data']['milestone'] or {}
        bug_dict = {
            'id': bug_id,
            'url': bug['data']['html_url'],
            'lang': 'scala',
            'type': None,
            'status': bug['data']['state'],
            'resolution': None,
            'summary': bug['data']['title'],
            'reporter': bug['data']['user']['login'],
            'versions': [milestone.get('title')],
            'labels': [label['name'] for label in bug['data']['labels']],
            'components': [],
            'created': bug['data']['created_at'],
        }
        new_bugs.append(bug_dict)
    return new_bugs


def transform_dotty(bugs):
    return transform_scala2(bugs)


def transform_java(bugs):
    new_bugs = []
    for bug in bugs:
        components = bug['data']['fields']['components'] or []
        versions = bug['data']['fields']['versions'] or []
        reporter = bug['data']['fields']['reporter'] or {}
        resolution = bug['data']['fields']['resolution'] or {}
        subcmp = bug['data']['fields'].get('customfield_10008', {}) or {}
        priority = bug['data']['fields']['priority'] or {}
        bug_dict = {
            'id': bug['data']['key'],
            'url': 'https://bugs.openjdk.java.net/projects/JDK/issues/' + bug['data']['key'],
            'lang': 'java',
            'type': bug['data']['fields']['issuetype']['name'].lower(),
            'status': bug['data']['fields']['status']['name'].lower(),
            'resolution': resolution['name'].lower() if 'name' in resolution else None,
            'summary': bug['data']['fields']['summary'],
            'reporter': reporter.get('displayName'),
            'versions': [v['name'] for v in versions],
            'labels': bug['data']['fields']['labels'] or [],
            'components': [v['name'].lower() for v in components],
            'subcomponents': subcmp.get('value', {}).get('name'),
            'created': bug['data']['fields']['created'],
            'priority': priority.get('name')
        }
        new_bugs.append(bug_dict)
    return new_bugs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang',
                        '-l',
                        required=True,
                        help="Engine to use: java, scala2, dotty, kotlin, groovy")
    parser.add_argument('--output',
                        '-o',
                        required=True,
                        help="Print output to this file")
    parser.add_argument('--input',
                        '-i',
                        required=True,
                        help="Load raw bug data from this file")
    args = parser.parse_args()

    bugs = load_bugs(args.input)
    fun = globals()['transform_' + args.lang]
    output = fun(bugs)
    save_bugs(args.output, output)


if __name__ == "__main__":
    main()
