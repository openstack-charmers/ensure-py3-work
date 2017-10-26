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

# scans all of the repos -- looking for python2 to 3 type stuff

import os
import re
import sys
import collections



ALL_DIR = './charms'

_CORE_PATTERN = "(?:'|\")(?:{})(?:'|\")"
_SINGLE_EQUALS = "(?:\s+\=\s+)"

PATTERNS = (
    # _CORE_PATTERN.format('|'.join(openstack_versions)),
    # _CORE_PATTERN.format('|'.join(ubuntu_releases)),
    "open\(.*\)",  # check that we are decoding the output to UTF-8
    "sorted\(.*cmp\=.*\)",  # cmp no longer supported, maybe use 'key'
    "\.sort\(.*cmp\=.*\)",  # cmp no longer suppored, maybe use 'key'
    "\.sort\(\)",  # convert to sorted()
    "UserDict",  # doesn't exist any more
    "print\ ",  # old style print statement
    "\"\ \%\ .*",  # using % when should be using .format(
    "set\(\[",  # set literal = {x, y, z}
    ".*\ /(?:\ .*|$)",  # single / no longer necessarily returns int
    "\ range\(.+\)",  # range might need to be xrange()
    "\.next\(\)",  # x.next() -> next(x)
    "class\ .*\(\)",  # old style classes might need to be object
    "\.iter[keys|items|values]\(\)",  # need changing to keys, etc.
    "\.[keys|items|values]\(\)",  # just need checking
)
REJECT_PATTERNS = (
    # "{}{}".format(_SINGLE_EQUALS, PATTERNS[0]),
    # "{}{}".format(_SINGLE_EQUALS, PATTERNS[1]),
)

print(PATTERNS)


def walk_py_files(directory, avoid_charmhelpers=True):
    for root, dirs, files in os.walk(directory):
        if avoid_charmhelpers and 'charmhelpers' in root:
            continue
        if ".tox" in root:
            continue
        for f in files:
            if f.endswith(".py"):
                yield os.path.join(root, f)


def scan_for_patterns(f):
    with open(f, "r") as fh:
        for count, l in enumerate(fh.readlines()):
            # print(len(l), l)
            for p_index, p in enumerate(PATTERNS):
                m = re.search(p, l)
                if m:
                    # print(m.group(0))
                    # see if we need to reject the line
                    # n = re.search(REJECT_PATTERNS[p_index], l)
                    # if not n:
                    yield count + 1, m.group(0), l


def main(args):
    found = collections.OrderedDict()
    top_level_dirs = sorted(os.walk(ALL_DIR).next()[1])
    print("Checking ...")
    for d in top_level_dirs:
        check_dir = os.path.join(ALL_DIR, d)
        found[d] = collections.OrderedDict()
        for f in walk_py_files(
                check_dir,
                avoid_charmhelpers=('charm-helpers' not in check_dir)):
            for line_num, match, line in scan_for_patterns(f):
                try:
                    found[d][f][line_num] = (match, line)
                except KeyError:
                    found[d][f] = collections.OrderedDict()
                    found[d][f][line_num] = (match, line)

    # Now print the report
    count = 0
    for d, packages in found.items():
        # print("Package/directory: {}".format(d))
        for package, lines in packages.items():
            # print("{} ... has {} changes".format(package, len(lines)))
            count += len(lines)

    print("Total packages needing changes: {}".format(len(found)))
    print("Total lines to change: {}".format(count))
    print("\nReport on lines to change and the match:")
    for d, packages in found.items():
        print("\nPackage/directory: {}".format(d))
        for package, lines in packages.items():
            print("    File: {}".format(package))
            for line_num, t in lines.items():
                # print("        {: >5}: {}".format(line_num, t[0]))
                print("        {: >5}: {}".format(line_num, t[1].strip()))


if __name__ == '__main__':
    main(sys.argv)