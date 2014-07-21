import subprocess
import sys
import cStringIO
import re
from collections import defaultdict

import satdown.utils
import satdown.format

from satdown.vendor.unidiff import parser

LOG_FORMAT = "%h%x00%an%x00%ad%x00%s%x00"
RE_TODO = re.compile("^\W*?TODO(?:\s|:)\s*(.*)$",re.MULTILINE)

def main(arguments):
    exit = 0
    changes = {}
    results = ((dir, logs(dir, arguments['since'])) for dir in arguments['repos'])
    for r in results:
        (dir, (success, output)) = r
        if not success:
            satdown.utils.error(
                "Couldn't run `git log` in '%s'" % dir,
                "(git says: '%s')" % output.rstrip()
            )
            exit = 1
        else:
            changes[dir] = process(dir, output)

    import pprint; pprint.pprint(satdown.format.SORT[arguments['sort']](changes))
    sys.exit(exit)

def logs(repo, since):
    cmd = [
        "git", "log",
        "--since=\"%s\"" % since,
        "--pretty=format:%s" % LOG_FORMAT,
        "--date=short"
    ]

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, cwd=repo
    )
    outputs = proc.communicate()
    rc = proc.returncode

    # Report status and stdout/stderr as appropriate.
    return (rc == 0, outputs[rc != 0])

def process(dir, log):
    return [process_commit(dir, commit) for commit in log.rstrip("\0").split("\0\n")]

def process_commit(dir, commit):
    sha, author, date, message = commit.split("\0")
    cmd = ["git", "diff-tree", "--diff-filter=ADM", "-M", "-p", "--root", sha]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=dir)
    diff, _ = proc.communicate()

    patchset = parser.parse_unidiff(cStringIO.StringIO(diff))
    todos = {}
    for patch in patchset:
        changes = defaultdict(list)
        for hunk in patch:
            new, old = set(hunk.target_lines), set(hunk.source_lines)
            added, removed = process_hunk(
                (i for i in hunk.target_lines if not i in old),
                (i for i in hunk.source_lines if not i in new)
            )

            if added or removed:
                changes['added'].extend(added)
                changes['removed'].extend(removed)
        if changes:
            todos[patch.path] = changes

    return (sha, author, date, message, todos)

def process_hunk(added, removed):
    return (search_lines(added), search_lines(removed))

def search_lines(lines):
    # TODO: Handle multi-line TODOs.
    matches = []
    for line in lines:
        r = RE_TODO.search(line)
        if r:
            matches.append(r.groups()[0])

    return matches
