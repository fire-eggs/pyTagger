#!/usr/bin/python
"""
====================================================================
Utility: delete all PyPhoto 2.0 "thumbs" thumbnail subfolders in 
an entire folder tree, in preparation for building newer 2.1
"_PyPhoto-thumbs.pkl" files on next folder opens.  Run this on 
your PyPhoto folders after upgrading to its 2.1 PyGadgets release.

Example use (Python 3.X or 2.X):

/MY-STUFF/Code$ python3 delete-pyphoto2.0-thumbs-folders.py
Root of folder tree to scan (Enter=".")? /MY-STUFF/Camera
Delete "/MY-STUFF/Camera/MERGED/PHOTOS/2006/thumbs" (y=yes)? n
	not deleted
Delete "/MY-STUFF/Camera/MERGED/PHOTOS/2007/thumbs" (y=yes)? y
Delete "/MY-STUFF/Camera/MERGED/PHOTOS/2008/thumbs" (y=yes)? n
	not deleted
Bye

This script is a frozen executable run directly in PyGadgets app 
and executable packages (on Macs, see PyGadgets.app/Contents/MacOS; 
on Windows you can run by clicking too):

.../PyGadgets.app/Contents/MacOS$ ./delete-pyphoto2.0-thumbs-folders

Older 2.0 subfolders are not deleted automatically, because their 
name is generic and may be used by other software (a former issue).

*Caution* - not all "thumbs/" are necessarily PyPhoto 2.0 folders,
so be careful to inspect the folders in each verify input prompt.
The learning-python.com/thumbspage program, for example, uses the
same name for the folder it generates and retains (unfortunately!). 
====================================================================
"""
from __future__ import print_function
import sys, os, shutil
if sys.version[0] == '2': input = raw_input

try:
    root = input('Root of folder tree to scan (Enter=".")? ') or '.'
except (EOFError, KeyboardInterrupt):
    print('No changes made.')
    sys.exit()  # ctrl-d/z or no stdin, or ctrl-c

for (dirhere, subshere, fileshere) in os.walk(root):
    for sub in subshere:
        if sub == 'thumbs':
            subpath = os.path.join(dirhere, sub)
            if input('Delete "%s" (y=yes)? ' % subpath).lower()[:1] == 'y':
                shutil.rmtree(subpath)
            else:
                print('\tnot deleted')

print('Bye')
