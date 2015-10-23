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
from time import time


def wait_for_files(pattern, min_age):
    while True:
        for path in glob(pattern):
            age = time() - getmtime(path)
            if age <= min_age:
                print('%s: only %.3gs old' % (path, age))
                sleep(min_age - age)
                break
        else:
            break


def main():
    from sys import argv
    pattern = argv[1]
    min_age = float(argv[2])
    wait_for_files(pattern, min_age)


if __name__ == '__main__':
    exit(main())
