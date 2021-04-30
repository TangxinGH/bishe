# https://gist.github.com/amitsaha/5990310

# !/usr/bin/python

import sys


# if len(sys.argv) !=3:
#     print 'Usage: tail.py <file> <nlines>'
#     sys.exit(1)

# fname, nlines = sys.argv[1:]

def tail(fname, nlines):
    # fname, nlines = ('./myspider/spiders/current_climb_progress.txt', 3)
    num_lines = int(nlines)

    with open(fname) as f:
        content = f.read().splitlines()

    count = len(content)
    for i in range(count - num_lines, count):
        content[i]
