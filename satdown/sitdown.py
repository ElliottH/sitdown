import subprocess
import sys

import satdown.utils

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
        cmd = ["git", "diff-tree", "-p", "--root", sha]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=dir)
        diff, _ = proc.communicate()
