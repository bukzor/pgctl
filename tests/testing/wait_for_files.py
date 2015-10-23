#!/usr/bin/env python
"""
This is a quick script that helps waiting for multiprocess coverage data.
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from glob import glob
from os.path import getmtime
from time import sleep
from time import time as now

inf = float('inf')


def format_time(timestamp):
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).strftime('%F %T.%f')


def wait_for_files(pattern, min_age):
    while True:
        max_mtime, max_path = max((getmtime(path), path) for path in glob(pattern))
        age = now() - max_mtime
        if age <= min_age:
            delta = min_age - age
            print('%s mtime:%s delta:%g %s: only %g old' % (
                format_time(now()),
                format_time(max_mtime),
                delta,
                max_path,
                age,
            ))
            min_age += delta
            sleep(min_age - age)
        else:
            break


def main():
    from sys import argv
    pattern = argv[1]
    min_age = float(argv[2])
    wait_for_files(pattern, min_age)


if __name__ == '__main__':
    exit(main())
