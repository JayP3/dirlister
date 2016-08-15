'''
Created on Dec 30, 2015

@author: jpierrepont
'''
try:
    from os import scandir, walk
except ImportError:
    from scandir import scandir, walk


def scantree3(path):
    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=False):
            for entry in scantree(entry.path):
                yield entry
        else:
            yield entry
            
def scantree(path):
    subs = []
    files = []

    for entry in scandir(path):
        try:
            if entry.is_dir(follow_symlinks=False):
                subs.append(entry)
            elif entry.is_file():
                files.append(entry)
        except OSError as e:
            print(e)
            continue
    yield (path, subs, files)

    for sub in subs:
        try:
            for x in scantree(sub.path):
                yield x
        except OSError:
            pass
            
def scantree2(path):
    subs = []
    files = []
    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=False):
            subs.append(entry)
        elif entry.is_file():
            files.append(entry)
    yield (path, subs, files)
    for sub in subs:
        scantree2(sub.path)

def scantree4(path):
    subs = []
    files = []
    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=False):
            subs.append(entry)
        elif entry.is_file():
            files.append(entry)
    yield (path, subs, files)
    for sub in subs:
        scantree2(sub.path)
        
if __name__ == '__main__':
    
    for root, subs, files in scantree2(r'C:\Users\jpierrepont\Desktop\aac'):
        for fname in files:
            print(fname.path)
     