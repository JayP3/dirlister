# ------------------------------------------------------------------------------
# Name:        countf.py
# Purpose:
#
# Author:      jpierrepont
#
# Created:     20/02/2015
# Copyright:   (c) jpierrepont 2015
# Licence:     <your licence>
# ------------------------------------------------------------------------------
import argparse
import os
import time
import logging

try:
    import scandir
except ImportError:
    scandir = os

# logging.basicConfig(filename='countf.log', level=logging.DEBUG)

ignore = ["~snapshot",  ".snapshot"]
tdircount = 0
tfilecount = 0


def print_to_fit(count, path):
    max = 80
    outp = ''
    outp += 'Files: '
    outp += str(count).ljust(15)
    remaining = max - len(outp)
    if len(path) > remaining:
        remaining -= 3
        pstr = path[0:(remaining / 2)] + '...' + path[-(remaining / 2):]
        outp += pstr
    print outp


def walk_path(path, gt=0, logfile='countf.log'):
    global tdircount
    global tfilecount
    flog = open(logfile, 'a')
#    for root, subs, files in os.walk(path):
    for root, subs, files in scandir.walk(path, followlinks=False):
        logging.debug('Checking %s', root)
        dircount = len(subs)
        fcount = len(files)

        if fcount > gt:
            pass
# print '#Files: %s\t%s' % (fcount, os.path.abspath(root))
#            print_to_fit(fcount, os.path.abspath(root))
        for sub in subs:
            if sub.lower() in ignore:
                print 'ignoring', os.path.join(root, sub)
        subs[:] = [x.lower() for x in subs if x.lower() not in ignore]
        logout = '{0}\t{1}\t{2}\t{3}\n'.format(time.ctime(), root,
                                               dircount, fcount)
        flog.write(logout)
#        print logout
        tdircount += dircount
        tfilecount += fcount
    flog.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('startpath', help='The path to start searching')
    parser.add_argument('--greaterthan', '-gt', type=int, default=0,
                        help='more than this  many files. Defaults to 0.')
    parser.add_argument('--logfile', '-l',
                        help='the logfile to write results to')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    stime = time.time()
    walk_path(args.startpath, args.greaterthan, logfile=args.logfile)
    print 'Finished in %.2f seconds' % (time.time() - stime)
    print '%d directories scanned' % (tdircount)
    print '%d files scanned' % (tfilecount)


if __name__ == '__main__':
    main()
