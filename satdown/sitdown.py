import subprocess
import sys
import cStringIO

import satdown.utils

from satdown.vendor.unidiff import parser

LOG_FORMAT = "%h%x00%an%x00%ad%x00%s%x00"

def main(arguments):
    exit = 0
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
            process(dir, output)

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
    for commit in log.rstrip("\0").split("\0\n"):
        sha, author, date, message = commit.split("\0")
        cmd = ["git", "diff-tree", "--diff-filter=ADM", "-M", "-p", "--root", sha]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=dir)
        diff, _ = proc.communicate()

        patchset = parser.parse_unidiff(cStringIO.StringIO(diff))
        for patch in patchset:
            for hunk in patch:
                new, old = set(hunk.target_lines), set(hunk.source_lines)
                added = [i for i in hunk.target_lines if not i in old]
                removed = [i for i in hunk.source_lines if not i in new]

                print("Added", added)
                print("Removed", removed)
