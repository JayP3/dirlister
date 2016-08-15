'''
Functions to sort and search through index files created by countf.py
'''

import os
import datetime
import glob
import tempfile
import argparse

test = r'\\napfileserver3\online_spider\#ONLINE_VIDEO_MPG_DONE'
log = 'countf.log'

# Constant variables related to the columns in an index file.
COLUMNS = 4
TSTAMP = 0
PATH = 1
DIRS = 2
FILES = 3


def counter(log, test):
    """
    Print the total number of nested files and subdirectories exist
    in a directory.
    """
    print 'Searching total number of directories and files in:\n\t%s' % (test)
    total_lines = 0
    dirs = 0
    files = 0
    with open(log, 'r') as f:
        for line in f:
            spltline = line.strip().split('\t')
            if len(spltline) != COLUMNS:
                continue
            if spltline[PATH].lower().startswith(test.lower()):
                files += int(spltline[FILES])
                dirs += int(spltline[DIRS])
            total_lines += 1
    print total_lines
    print 'total nested subdirectories:', dirs
    print 'total nested files:      ', files


def find_many_files(log, number):
    """Print the number of files in a directory"""
    print '\nSearching for directories with more than %d files.' % (number)
    print '-' * 70, '\n'
    linec = 1
    with open(log, 'r') as f:
        for line in f:
            spltline = line.strip().split('\t')
            if len(spltline) != COLUMNS:
                print 'error on line', linec
            try:
                files = int(spltline[FILES])
                if files > number:
                    print spltline[TSTAMP], spltline[FILES], spltline[PATH]
            except ValueError:
                print 'ValueError on line', linec
            except IndexError:
                print 'IndexError on line', linec
            linec += 1


def subdirs(log, path):
    """
    Find the count of files and directories directly in a
    particular directory path
    """
    print 'Finding Info for', path
    with open(log, 'r') as f:
        for line in f:
            spltline = line.strip().split('\t')
            if len(spltline) != COLUMNS:
                continue
            lpath = spltline[PATH]
            if path.lower() == lpath.lower():
                dirs = int(spltline[DIRS])
                files = int(spltline[FILES])
                print 'Subfolders:', dirs
                print 'Files:     ', files
            else:
                pass


def find_many_dirs(log, number):
    print '\nSearching for directories with more than %d subdirectories.'\
          % (number)
    print '-' * 70, '\n'
    linec = 1
    with open(log, 'r') as f:
        for line in f:
            spltline = line.strip().split('\t')
            if len(spltline) != COLUMNS:
                print 'error on line', linec
            try:
                dirs = int(spltline[DIRS])
                if dirs > number:
                    print spltline[TSTAMP], spltline[DIRS], spltline[PATH]
            except ValueError:
                print 'ValueError on line', linec
            except IndexError:
                print 'IndexError on line', linec
            linec += 1


def find_objects(log, number, files=True, dirs=True):
    print '\nSearching for directories containing more than %d combined files \
and folders.' % (number)
    print '-' * 70, '\n'
    linec = 1
    with open(log, 'r') as f:
        for line in f:
            spltline = line.strip().split('\t')
            if len(spltline) != COLUMNS:
                print 'error on line', linec
            try:
                dirs = int(spltline[DIRS])
                files = int(spltline[FILES])
                if dirs + files > number:
                    print spltline[TSTAMP], dirs + files, spltline[PATH]
            except ValueError:
                print 'ValueError on line', linec
            except IndexError:
                print 'IndexError on line', linec
            linec += 1


def sort_small_index_file(fn):
    """Read a text file into a list. Sort it. Write it back to the file."""
    with open(fn, 'r+') as f:
        lines = f.readlines()
        lines.sort(key=lambda x: x.split('\t')[PATH])
        f.seek(0)
        f.truncate()
        f.writelines(lines)


def ctime_to_datetime(ct):
    """Convert a time.ctime timestamp to a python datetime object"""
    dt = datetime.datetime.strptime(ct, '%a %b %d %H:%M:%S %Y')
    return dt


def delete_duplicates(fn):
    """
    Deletes duplicate directory listings in the index file.
    Should be used in a sorted index file. Using in an unsorted file will
    not correctly delete duplicates.
    """
    _id, tmp = tempfile.mkstemp()
    prev = ['', '', '', '']

    with open(fn, 'r+') as f:
        with open(tmp, 'w+') as ftmp:
            for line in f:
                timestamp, path, dirs, files = line.split('\t')
                # if the directory path is the same as on the prevcious line
                if path.lower() != prev[PATH].lower():
                    if all(prev):
                        ftmp.write('\t'.join(prev))
                    prev = [timestamp, path, dirs, files]
                else:
                    cur_timestamp = ctime_to_datetime(timestamp)
                    prev_timestamp = ctime_to_datetime(prev[0])
                    if cur_timestamp > prev_timestamp:
                        prev = [timestamp, path, dirs, files]

            if all(prev):
                ftmp.write('\t'.join(prev))

            ftmp.flush()
            f.seek(0)
            f.truncate()
            ftmp.seek(0)
            for line in ftmp:
                f.write(line)


def sort_large_index_file(fn):
    """
    Breaks a large index file out into smaller files, sorts the smaller files,
    then rewrites the main file.
    """
    outdir = tempfile.mkdtemp()
    count = 0
    # delete any pre-existing temp files
    # may not need this after switching to tempfile module
    for i in glob.glob(os.path.join(outdir, '*')):
        os.remove(i)
    # write files for each file share to a new, temp file
    with open(fn, 'r') as f:
        for line in f:
            spltline = line.strip().split('\t')
            if len(spltline) != COLUMNS:
                continue
            p = spltline[PATH]
            p = p.strip(os.sep)
            share = p.split(os.sep)
            outf = '-'.join(share[:2])
            tmpfile = os.path.join(outdir, outf)
            with open(tmpfile, 'a') as of:
                of.write(line)
            count += 1
            if count % 10000 == 0:
                print '\rlines done:', count,
    print
    # sort each of those temp files, and write them back to the original file.
    with open(fn, 'w') as f:
        smallfiles = [os.path.join(outdir, x) for x in os.listdir(outdir)]
        smallfiles.sort()
        for fname in smallfiles:
            sort_small_index_file(fname)
            for line in open(fname):
                f.write(line)


def sort_index_file(fn, limit=200000):
    """
    Sort an index file. If the file is larger than the set limit,
    a.k.a. too large to sort in memory, split into smaller files,
    sort them, then use the results to build the final sorted file.
    """
    size = os.path.getsize(fn)
    if size > limit:
        sort_large_index_file(fn)
    else:
        sort_small_index_file(fn)
        
def combine(f1, f2):
    '''Add contents of f1 to f2'''
    with open(f1) as fsource:
        with open(f2, 'a') as fdest:
            for line in fsource:
                fdest.write(line)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'indexfile', help='The index file you want to work with.')
    parser.add_argument(
        '--sort', '-s',
        action='store_true',
        help='Sort the entries in the index file by directory path')
    parser.add_argument(
        '--dedupe', '-d',
        action='store_true',
        help='Delete duplicate entries for a filepath. \
        Index should be sorted first.')
    parser.add_argument(
        '--finddirs', '-x',
        type=int,
        help='find directories with more than n number of subdirectories')
    parser.add_argument(
        '--findfiles', '-f',
        type=int,
        help='find directories with more than n number of files')
    parser.add_argument(
        '--both', '-b',
        type=int,
        help='find directories with more than n number of combined\
        files and directories')
    parser.add_argument(
        '--countall', '-c',
        type=str,
        help='Count all nested files and subdirectories in a given path.')
    parser.add_argument(
        '--subdirs', '-i',
        type=str,
        help='Count all files and subdirectories in a given path.')
    parser.add_argument('--combine', '-cb', nargs=2,
                        help='combine two index files into one' )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    if args.sort:
        print 'sorting'
        sort_index_file(args.indexfile)
    if args.dedupe:
        print 'deduping'
        delete_duplicates(args.indexfile)
    if args.finddirs:
        print 'find dirs', args.finddirs
        find_many_dirs(args.indexfile, args.finddirs)
    if args.findfiles:
        print 'find files', args.findfiles
        find_many_files(args.indexfile, args.findfiles)
    if args.both:
        print 'find files and directories'
        find_objects(args.indexfile, args.both)
    if args.countall:
        print 'countall', args.countall
        counter(args.indexfile, args.countall)
    if args.subdirs:
        subdirs(args.indexfile, args.subdirs)
    if args.combine:
        src, dst = args.combine
        print 'writing contents of %s to %s' % (src, dst)
        combine(src, dst)


if __name__ == '__main__':
    main()


# find_many_files(log, 80000)
# find_many_dirs(log, 80000)
# find_objects(log, 80000)
# counter(log, r'\\napfileserver3\online_video')
# subdirs(log, r'\\napfileserver3\online_video')
# delete_duplicates('countf2.log')
# sort_index_file('countf2.log')
