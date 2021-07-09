# ensure-py3-work

**Note: this is now archived as it's no longer needed and is only being kept for historical reference.**

This is a collection of utilities and, during the project, the status of
the ongoing work to migrate the non-reactive charms from Python 2 to
Python 3.

**Note these scripts expect to run under python3**.

## Usage

There are 4 python files in the repository.  **You probably only need to
use `get_charms.py` and `scan_repos.py`**.  For completeness, all are
described.

* `github_fetcher.py` - this fetches json documents for the metadata of
  all the projects in the 'openstack' organisation to the `./all_repos.json`
  file.  It's unlikely that this will be needed as the `all_repos.txt`
  file has been generated and added to the repo.

  **Note: you need to configure things in this script for your own GITHUB
  authentication.**

* `parse-github-json.py` - this scans the json documents and gets the
  charm github repository links and saves them in `all_repos.txt`.  Again,
  **it's unlikely that you need to run this, unless things have
  significantly changed in terms of the number of charm repos that
  exist.**

* `get_charms.py` - uses the all_repos.txt from above, to fetch all of the
  identitied repositories and fetches them into a `charms/` subdirectory.
  If the charms have already been fetched, then it refreshes them.  It
  takes a single argument, which is the branch to checkout.  Normally,
  this will be master.

  `./get_charms.py master`

* `scan_repos.py` - uses regexs to scan the source of the charms to find
  possible Python2 to Python3 issues. It takes a single argument which is
  either `--all` to scan all the charm directories, or `{charm name}`
  (without the `charm-` prefix) to just scan a single file.

  `./scan_repos.py --all | less`
  `./scan_repos.py ceph-mon | less`

## Things to check for when migrating a charm from Py2 -> Py3

1. The tox.ini targets will need changing; these are still being
   determined.
2. Be careful of relative imports in Py2 files; absolute imports are the
   only thing available.
3. Remember that anything that returns a `dict` should probably return
   a `collections.OrderedDict()` unless you are **sure** the ordering of
   the dictionary doesn't matter.  This might also require changes to
   associated tests.

The relevant snippet from the `scan repos.py` file is:

```python
PATTERNS = (
    # _CORE_PATTERN.format('|'.join(openstack_versions)),
    # _CORE_PATTERN.format('|'.join(ubuntu_releases)),
    "\#\!/usr/bin/python",
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
    "\.iter(?:keys|items|values)\(\)",  # need changing to keys, etc.
    "\.(?:keys|items|values)\(\)",  # just need checking
    "json\.loads\(",  # in case it's the output of a check_output() call
    "check_output\(",  # all checkout calls have to be looked at
    "\.message",  # this is looking for "e.message" for exceptions; just need
                  # checking.
    "= \{\}",  # look for empty dictionary assignements.  Do they need to go
               # to collections.OrderedDict()
)
```

Note that the script detects symlinks and doesn't scan them as it assumes
that they link to a file.

4. Anything returning `.items()`, `.values()`, or `.keys()` might need to
   return `list(x.keys())` as Py3 returns iterator-like objects instead of
   lists.

5. Anything to do with files (`open(...)` and friends) may have
   bytestring, unicode issues.  Note, that the default on Python3 is to
   open files in 'text' mode, which is already unicode aware.  It's only
   if the file is being opened or used in binary mode that difficulties
   arise.

6. Anything returned from `subprocess.check_output(...)` and friends,
   needs to be decoded from a bytestring to a str using
   `x.decode('UTF-8')`.

7. When charms upgrade:  It's **likely** that the upgrade hook will need
   to be shimmed so that relevant Python3 apt libraries can be installed
   in the same way that the install hook has a shim to install some
   python2 apts.

## Authors experience

The hardest part is getting the absolute imports working with how the
unit-tests are mocking out dependencies.  This is particularly the case
with mocking somehting *before* the file is imported (e.g.
`hookenv.config(...)`, `register_configs(...)` and hardening functions.
I don't have a good solution to this yet; it's very much trial and error).
I'll keep updating the experience here.
