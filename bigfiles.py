#!/usr/bin/env python
"""
    bigfiles.py
    ~~~~~~~~~

    A python script which reports the largest <N> files
    for each set of directories passed to the script.

        python bigfiles.py -n5 /home/stu /home/rob

        ^-- show the five largest files in /home/stu and
            the five largest files in /home/rob
        
        python bigfiles.py -d -n15 /var/www

        ^-- show the largest 15 directories, as determined by
            files directly under them (sub-dirs not counted)

        
    Stuart Powers
    http://sente.cc/
"""


import sys
import os
import os.path
import stat
import fnmatch

from optparse import OptionParser
from operator import itemgetter, attrgetter
from stat     import ST_MODE,S_ISDIR,S_ISREG,S_ISLNK,ST_SIZE
from heapq    import heappush, heappop


def humanize(bytes):
  """Turns a byte count into a human readable string."""
  if bytes > 1099511627776:
    value = bytes / 1099511627776.0
    units = "TB"
  elif bytes > 1073741824:
    value = bytes / 1073741824.0
    units = "GB"
  elif bytes > 1048576:
    value = bytes / 1048576.0
    units = "MB"
  elif bytes > 1024:
    value = bytes / 1024.0
    units = "kB"
  else:
    value = float(bytes)
    units = "bytes"
  return "%.2f %s" % (value, units)


usage = "usage: %prog [options] arg"
parser = OptionParser(usage)

parser.add_option("-n", "--num", "--number",
                dest="num",
                type="int",
                default=10,
                action="store",
                help="Display <count> results"
                )

parser.add_option("-B", "--bytes",
                dest="human",
                action="store_false",
                default=True,
                help="display file sizes in bytes, opposed to a human readable format (kB/MB/GB)"),

parser.add_option("-d", "--directories",
                dest="check_dirs",
                action="store_true",
                default=False,
                help="report the largest directories, determined by summing the filesize of each directories' immediate children",)

parser.add_option("--filter", "-f",
                dest="filter_pattern",
                type="string",
                action="store",
                default="*")

parser.add_option("--maxdepth", "--depth",
                dest="maxdepth",
                type="int",
                action="store",
                default="0",
                help="Do not recurse more than <depth> levels deep")

parser.add_option("--EXPERIMENTAL", "--EXP", "--test", "--dev",
                dest="EXPERIMENTAL",
#                type="",
                action="store_true",
                default=False,
                help="Experimenta"),

(options, args) = parser.parse_args()

#print options,args
num=options.num
human=options.human
filter_pattern=options.filter_pattern
check_dirs=options.check_dirs
maxdepth=options.maxdepth
EXPERIMENTAL=options.EXPERIMENTAL

if len(args) == 0:
    args.append(".")


def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = len([x for x in some_dir if x == os.path.sep])
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = len([x for x in root if x == os.path.sep])
        if num_sep + level <= num_sep_this:
            del dirs[:]


def walk_level(some_dir,maxdepth=0,group_directories=0):
    level=maxdepth
    if maxdepth == 0:
        level=999

    for root,dirs,files in walklevel(some_dir, level):
        rootsize=os.stat(root)[ST_SIZE]
        for f in files:
            try:
                fn = os.path.join(root, f)
                ss=os.stat(fn)
                rootsize+=ss[ST_SIZE]
                if not group_directories:
                    yield (ss[ST_SIZE], fn)
            except:
                pass
        if group_directories:
            yield (rootsize,root)


def search(path):
    heap=[]
    ordered=[]

    for item in walk_level(os.path.normpath(path),
            maxdepth,
            group_directories=check_dirs):
        heappush(heap,item)

    while heap:
        ordered.append(heappop(heap))
    for element in ordered[:-num-1:-1]:
        if human:
            print "%s\t%s" % (humanize(element[0]), element[1])
        else:
            print "%s\t%s" % (element[0], element[1])


if __name__ == '__main__':
    for path in args:
        search(path)

