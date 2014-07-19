#!/usr/bin/env python

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

import os
import sys

# Nasty trick to import the package we are in.
a_file = os.path.abspath(os.path.realpath(__file__))
a_dir = os.path.split(a_file)[0]
p_dir = os.path.split(a_dir)[0]
sys.path.insert(0, p_dir)

try:
    # Import goes here
    from satdown.vendor.docopt import docopt
    from satdown.version import VERSION
    from satdown.sitdown import main
    import satdown.utils
except ImportError:
    # Perhaps we are being run through a soft link.
    sys.path = [a_dir] + sys.path[1:]
    from satdown.vendor.docopt import docopt
    from satdown.version import VERSION
    from satdown.sitdown import main
    import satdown.utils

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
        'repos': satdown.utils.uniq(arguments['REPOSITORY'])
    })
