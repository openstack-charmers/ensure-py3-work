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

import os
import subprocess
import sys

ALL_REPOS_FILE = 'all_repos.txt'
CHARM_PREFIX = "./charms/"


def clone_repos(file, branch):
    with open(file, 'r') as f:
        repos = f.readlines()
    print("Doing {} repos".format(len(repos)))
    # split off the charm name from the repo
    for repo in repos:
        charm_name = repo.split('/')[-1].split('.')[0]
        print("Doing {} download".format(charm_name))
        if charm_name.startswith("charm_"):
            charm_name = charm_name[6:]
        charm_dir = CHARM_PREFIX + charm_name
        if os.path.exists(charm_dir):
            cmd = ("cd {charm} && "
                   "git fetch origin && "
                   "git checkout {branch} && "
                   "git merge --ff-only origin/{branch}"
                   .format(charm=charm_dir, branch=branch))
            subprocess.check_call(cmd, shell=True)
        else:
            cmd = "git clone {} {}".format(repo.rstrip('\n'), charm_dir)
            subprocess.check_call(cmd.split(' '))
            cmd = "cd {} && git checkout {}".format(charm_dir, branch)
            subprocess.check_call(cmd, shell=True)


def main(argv):
    if len(argv) < 2:
        print("usage: get-charms <master || stable/nn.nn>")
        exit(1)
    branch = argv[1]
    clone_repos(ALL_REPOS_FILE, branch)


if __name__ == '__main__':
    main(sys.argv)
