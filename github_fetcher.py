#!/usr/bin/env python3
# Copyright 2017 Canonical Group Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# Fetch all of the github openstack organisation repos into one file
import requests
import json
import os


URL = "https://api.github.com/organizations/324574/repos?page={}"
FIRST = 1
LAST = 52
FILE = "./all_repos.json"
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME')


def fetch(page):
    return requests.get(URL.format(page), auth=(GITHUB_USERNAME, GITHUB_TOKEN))


def main():
    print(fetch(1).text)
    all_repos = []
    for page in range(FIRST, LAST + 1):
        print("Fetching page {}".format(page))
        all_repos.extend(json.loads(fetch(page).text))

    # write the result to a file
    print("Writing file")
    with open(FILE, 'w') as f:
        json.dump(all_repos, f)
    print("Done!")


if __name__ == '__main__':
    main()
