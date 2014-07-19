"""
Let your repositories work for you.

Usage:
  sitdown [--since=<when>] [--sort=<by>]
  sitdown [--since=<when>] [--sort=<by>] REPOSITORY ...
  sitdown (-h | --help)
  sitdown --version

Arguments:
    REPOSITORY      One or more git repositories to run in [default: .].

Options:
  --since=<when>    When to generate the report from [default: last monday].
  --sort=<by>       What to sort the report by
                    (one of: date, author, directory [default: date]).
  -h --help         Show this screen.
  --version         Show version.

"""
from vendor.docopt import docopt
import os

from version import VERSION
from sitdown import main
import utils

if __name__ == '__main__':
    arguments = docopt(__doc__, version=VERSION)
    if not arguments['REPOSITORY']:
        # Default to the current directory.
        arguments['REPOSITORY'].append(os.getcwd())
    else:
        # Make everything absolute.
        arguments['REPOSITORY'] = [os.path.abspath(repo) for repo in arguments['REPOSITORY']]

    # Pass on the options needed.
    main({
        'since': arguments['--since'],
        'sort':  arguments['--sort'],
        'repos': utils.uniq(arguments['REPOSITORY'])
    })
