#!/usr/bin/env python3
import json

FILE = "./all_repos.json"


def read_json(file):
    with open(file, 'r') as f:
        return json.load(f)


def main():
    all_repos = read_json(FILE)
    for r in all_repos:
        name = r['full_name']
        if (name.startswith('openstack/charm-') and
                '-specs' not in name and '-guide' not in name):
            print(r['git_url'])


if __name__ == '__main__':
    main()
