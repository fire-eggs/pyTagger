"""
===============================================================================
viewer_thumbs.py (part of the PyPhoto 2.2 program in PyGadgets)

Copyright: 2017-2018 by M. Lutz, from book "Programming Python, 4th Edition".
License: provided freely, but with no warranties of any kind.
Requires Pillow (PIL) for both JPEGs and thumbnail-image creation and use.

===============================================================================
OVERVIEW
===============================================================================

THIS MODULE creates thumbnail images for all the images in a folder, as 
either a single pickle file, or individual files in a subfolder.  It is 
used by PyPhoto to collect image thumbnails to be displayed; PyPhoto 
also adds thumbs scrolling, and much more functionality.  Other programs 
(e.g., thumbspage) may also use this module to build thumbnail files.
The simple viewer in this file's __main__ displays all images in a folder
as thumbnail image buttons that display the full image when clicked.  

THUMBNAIL CACHING is crucial for speed in PyPhoto and others, given the 
relative slowness of Pillow's thumbnail generator.  Though some of this
slowness may be due to image-file IO, most seems to stem from Pillow; its
Image.load() is not called explicitly in code here.  That said, Pillow has
lower-quality filters that would likely run faster, but PyPhoto by design 
uses the Pillow filter that runs slowest but yields best quality thumbs.

To neutralize the thumb-creation cost, the code here used by PyPhoto saves
a folder's thumbs in a pickle-file cache on first folder open.  After the 
first open creates this cache, later opens are nearly instantaneous, because
they load very small prebuilt thumbnail images from the file.  Programs that
use individual prebuilt thumb files in subfolders are similarly accelerated.
In both storage models, the cache is also auto-updated as photos are edited, 
deleted, renamed, or added, so it remains in synch with actual images. 

The natural alternative to thumbs caching (used by some file explorers) 
attempts to make thumbnails only for the image files currently in view.
This isn't used here due to both its complexity in Tk, and its unavoidable 
consequence of lag as the view is changed/scrolled.  With caching, there
is never any noticeable lag, except during the first folder open.

Caching is also important for programs which use this module to create a
a folder of thumb images during development - the original mode coded here.
The web pages built by the thumbspage program, for instance, open quickly
because they use thumb files prebuilt before any user interaction happens. 
Folder mode is still supported here, though it's no longer kept as current,
and thumbspage now uses a custom version of the forked code here, with 
changes propagated as needed (see learning-python.com/thumbspage.html).

===============================================================================
VERSIONS
===============================================================================

This section documents changes in this file related to PyPhoto versions.

VERSION 2.2, Sep-2018: rereleased with new PyGadgets packages. 

  This version borrows two changes from thumbspage, and adds one of its own.

  1) This version adds auto-rotation of images with "Orientation" Exif tags, 
     to display both images and thumbnails right-side up.  This is useful for 
     commonly tilted images shot on smartphones.  Thumbnails are stored in 
     corrected form permanently in their cached files, but full-size images 
     are rotated in memory only (PyPhoto does not change source-image files).

  2) This version adds a workaround for a Pillow too-many-open-files bug
     (mostly for Mac OS source code), which requires manual image-file opens
     and closes.  Both this and the prior item were inspired by (copied from)
     the related thumbspage program and project; see its URL above - its own
     viewer_thumbs.py has additional documentation on both changes.

  3) Unique here: 2.2 also works around an obscure issue in older Pillows that 
     ignore image.name filenames if a buffer object is passed to image.save().
     These Pillows wind up raising KeyErrors for key '' when trying to fetch
     format type.  This does not occur in the Pillow used to make PyPhoto apps, 
     but it can when running source code.  The fix is to manually pass in a 
     format derived from the filename, aping what later Pillows do correctly.
     See getImageFormat() for more details.  This isn't required in thumbspage,
     because all its image.save() calls pass in filename strings, not buffers. 

VERSION 2.1, Nov-2017: rereleased with new PyGadgets packages.  

  Most prominently in 2.1, this module now stores all the thumbnails for a
  folder in a single pickle file, instead of individual image files in a 
  subfolder.  This avoids:

  1) Expanding image trees with many extra files (15k images formerly meant 
     15k thumb files), which puts an extra burden on data archiving jobs

  2) Multiple file loads and saves (1 versus N) which may or may not improve 
     folder open speed (see Performance below), but reduces filesystem access

  3) A nasty modtime-copy issue for backup programs (copying image modtimes
     to thumb files to detect image changes can defeat timestamp-based programs
     like Mergeall if thumb size is changed but source-image content is not)

  Thumbs-file filename:

    The thumbs pickle file is named "_PyPhoto-thumbs.pkl" and shows up in each 
    writeable folder opened by PyPhoto.  Its "_" sorts uniquely, but it is not  
    named with a leading ".' because hidden files can be problematic for data 
    archiving programs (e.g., Mergeall should propagate these files too), and 
    covert content is both condescending and rude (you should be allowed to 
    see what programs do to your computer).

  Thumbs-file performance:

    The new single pickle-file mode has no noticeable performance differences.
    It runs at almost exactly the same speed and requires almost exactly the
    same storage space as the former subfolder mode.  Pickle-file mode can take
    up slightly more space for very large folders, but the difference is fully 
    trivial.  For example, the pickle file of an 1,100-photos folder checked in
    at just 60k more space than its subfolder equivalent (of 3.8M total size); 
    it also was built in the same number of seconds (per timing with PyClock).

  Thumbs-file compatibility:

    This change is not backward compatible.  Version 2.1's new files are the 
    default, and are always used by PyPhoto.  Version 2.0 subfolders are no 
    longer created or used unless requested explicitly by client code, and are 
    _not_ auto-deleted or auto-converted to the 2.1 pickle-file format when 
    found (2.0's too-generic subfolder name "thumbs" may have other uses). 

    PyPhoto 2.0 users should run the included script (or its frozen executable)
    "delete-pyphoto2.0-thumbs-folders.py" to delete all 2.0 subfolders when 
    upgrading to 2.1.  Else 2.0's subfolders will remain as unused trash after
    2.1's files are generated on folder opens.  Mac app users: run the delete
    executable in PyGadgets.app/Contents/MacOS (see Show Package Contents).

    Version 2.0 subfolder creation and use is still supported as an option,
    however, for use by other programs that require explicit thumb files (e.g.,
    learning-python.com/thumbspage, though that program's version is now unique).
    Mixed-mode use is not supported: client code must use the default 2.1 file 
    xor request 2.0 subfolders for thumbnail-image storage.

  Other 2.1 changes:

    Version 2.1's pickle-file mode (only) also now:

    1) Names the pickle file with a '_PyPhoto' prefix, to clarify its source.
       This file is the only artifact of the program, and can be deleted freely.

    2) Explicitly sorts image-dir names, to avoid os.listdir() platform diffs.  
       Lowercase mapping emulates the ordering on Macs (Windows and Linux differ)

    3) Uses a placeholder thumb for images whose thumb create failed (don't omit!).
       This requires pyphoto.py to also catch later failures for image open too.

    4) Works for unwriteable folders (e.g., BD-R discs): thumb saves are simply
       skipped, but the folder may open _very_ slowly due to thumb recreations

    5) Allows image-change detection to be turned off, to avoid full thumbnail 
       regens when file modtimes are skewed between filesystems or platforms.  
       Intended for large, static archives where thumb regens would be slow.
       Modtimes are brittle - see Mergeall's related DST and time-zone issues: 
       http://learning-python.com/mergeall-products/unzipped/UserGuide.html#dst

       In practice, modtime skew has not proven to be an issue for archives 
       burned to BD-Rs, used on a single platform, or transferred between 
       Mac OS and Windows on exFAT drives.  Other contexts may not fare as
       well; dual-boot Linux systems, for example, may have modtime skew.

    Note that 2.0's subfolder mode does _not_ have these other 2.1 features;
    PyPhoto is the main client, and thumbspage is still using a prior version
    (its version of this file eventually followed an evolution all its own).

  Other thumbs options considered:

    1) A JSON file.  Downsides: binary data is not directly supported, though 
       encoding as latin-1 suffices; takes more space due to '\' text escapes. 

    2) Zipping the original subfolder.  Downsides: may be slower, though in the
       end the file-save bytes pickle seems similar to an uncompressed zipfile;
       requires writeable device access plus cleanup for temp unzips.

VERSION 2.0, Sep-2017 [SA]: standalone release of book's PyGadgets.

  Part of the standalone PyGadgets release of PyCalc, PyClock, PyPhoto, PyToe.
  Multiple changes were made to the original code in PP4E, both here and in 
  pyphoto.py; search for label "[SA]" to find all 2.0 changes made.

===============================================================================
"""

import os, sys, math, mimetypes, shutil, errno, pickle, traceback, io
import base64 # KBR watermark images
from tkinter import *
import pillow_avif                # KBR avif support
#KBR TODO doesn't work import pillow_svg.SvgImagePlugin  # KBR svg support
from PIL import Image                   # <== required for thumbs
from PIL.ImageTk import PhotoImage      # <== required for JPEG display
from PIL.ExifTags import TAGS           # <== required for orientation tag [2.2]

tagwin = None

###############################################################################
# Choose your weapon (use 2.1 file or 2.0 subdir mode)
###############################################################################


def makeThumbs(imgdir,                            # source dir, actual images
               size=(100, 100),                   # max size, all thumbs (or 128?)
               subdir='thumbs',                   # 2.0 image-files subfolder 
               pklfile='_PyPhoto-thumbs.pkl',     # 2.1 pickle-file thumbnails
               forceSubdir=False,                 # True=make and use subfolders
               busywindow=None,                   # Tk widget: announce pause in GUI?
               nothumbchanges=False,              # 2.1 ignore diffs in images? (BD-R)
               _tagswin=None):

    global tagwin
    tagwin = _tagswin

    if forceSubdir:
        thumbs = makeThumbs_subdir(imgdir, size, subdir, busywindow)
    else:
        thumbs = makeThumbs_pklfile(imgdir, size, pklfile, busywindow, nothumbchanges)
    return thumbs


###############################################################################
# [2.1] Newer pickle-file thumbs storage default (single file)
###############################################################################


# This variant uses isImageFileName() and modtimeMatch() of original below


def getExifTags(imgobj):
    """
    --------------------------------------------------------------------------
    [2.2] Collect image-file metadata in a new dict, if any (else empty).
    This stores each tag value present under its mnemonic string name, by 
    mapping from image tag numeric ids to names, via the PIL.ExifTags table.
    --------------------------------------------------------------------------
    """
    tags = {}
    try:
        info = imgobj._getexif()                    # not all have Exif tags
        if info != None:
            for (tagid, value) in info.items():
                decoded = TAGS.get(tagid, tagid)    # map tag's id to name 
                tags[decoded] = value               # use id if not in table
    except Exception as E:
        pass
    return tags


def reorientImage(imgobj):
    """
    --------------------------------------------------------------------------
    [2.2] Rotate an image to be right-side up (top-side-top) if needed.
    In PyPhoto, this is used for both thumbnail images stored in files, 
    and full-size images in memory.  Unlike thumbspage, PyPhoto never 
    changes full-size image files, and requires no backup-copy protocol.
    This is mostly an automatic alternative to manually rotating images 
    before making thumbs, but is useful for smartphone and other photos.
    Note: this uses transpose(), not rotate(); the latter may change more.
    --------------------------------------------------------------------------
    """
    tags = getExifTags(imgobj)                      # not all have Exif tags
    orientation = tags.get('Orientation')           # not all have this tag
    if orientation:

        transforms = {
            # other settings don't make sense here
            1: None,                # top up (normal)
            3: Image.ROTATE_180,    # upside down
            6: Image.ROTATE_270,    # turned right
            8: Image.ROTATE_90      # turned left
        }

        transform = transforms.get(orientation, None)     # not all tag values used
        if transform != None:
            print('--Reorienting tilted image')
            try:
                imgobj = imgobj.transpose(transform)      # rotate to a new copy
            except:
                traceback.print_exc()
                print('--Transform failed: skipped')      # punt: can't auto fix

    return imgobj   # new or original


def openImageSafely(imgpath):
    """
    --------------------------------------------------------------------------
    [2.2] Work around a Pillow image auto-close bug, that can lead to 
    too-many-open-files errors in some contexts (most commonly when 
    running source code on Mac OS, due to its low #files ulimit).  The
    fix is to simply take manual control of file opens and saves.  For
    more details, see this code's source in the same-named thumbspage 
    file, at https://learning-python.com/thumbspage/viewer_thumbs.py.
    --------------------------------------------------------------------------
    """
    fileobj = open(imgpath, mode='rb')          # was Image.open(imgpath)
    filedat = fileobj.read()
    fileobj.close()                             # force file to close now
    imgobj = Image.open(io.BytesIO(filedat))    # file bytes => pillow obj
    return imgobj


def getImageFormat(imgname):    # imgobj no longer used
    """
    --------------------------------------------------------------------------
    [2.2] Work around a Pillow image-format issue, that can lead to KeyError
    exceptions in older versions of Pillow.  These Pillows ignore image.name,
    set here for images loaded from buffer objects.  This is not an issue for 
    PyPhoto apps (which use a later Pillow), but may be for source-code users 
    with older installs.  To work around, pass to image.save() an image format 
    derived from image file name, aping what later Pillows do automatically.

    Note that it's _almost_ equivalent to use imgobj.format (the result of 
    Pillow's "guess" when opening the image object) instead of filename 
    analysis, but not quite.  This field works for some image types; and is 
    MPO for some JPEGs, which works anyhow; but is None for oriented JPEGs,
    which triggers the same Pillow KeyError exception this fix addresses...

    Also note that name analysis assumes that PIL's extensions table has been
    filled by its plugins machinery (via its init()).  registered_extensions() 
    forces initialization if needed, but this call is not present in the 
    older Pillows this workaround seeks to address; assume init() is run.
    --------------------------------------------------------------------------
    """
    try:
        from PIL.Image import registered_extensions    # where available
        EXTENSION = registered_extensions()            # ensure plugins init() run
    except:
        from PIL.Image import EXTENSION                # else assume init() was run

    ext = os.path.splitext(imgname)[1].lower()         # lookup ext in Pillow table
    format = EXTENSION[ext]                            # fairly brittle, this...
    return format


def sortedDisplayOrder(imgdir):
    """
    ---------------------------------------------------------------------------
    Sort os.listdir() result per Python code, so it's the same on all
    platforms.  The lowercase mapping emulates Mac OS ordering; Windows
    differs by case, and Linux differs widely.  Factored here for use in
    pyphoto.py: its Next/Prior order must agree with thumbs-display order.
    ---------------------------------------------------------------------------
    """
    return sorted(os.listdir(imgdir), key=str.lower)   # a list, not an iterable


def findPlaceholder(filename='noimage.png'):
    """
    ---------------------------------------------------------------------------
    Locate the placeholder thumb image used for all failed image files.
    This has to work in every run context, and does: see next function.
    ---------------------------------------------------------------------------
    """
    tries = ['.', '../..', os.path.dirname(__file__)]
    for atry in tries:
        path = os.path.join(atry, filename)
        print(path)
        if os.path.exists(path):
            return path, filename
    return None, None


def makeThumbs_pklfile(imgdir, size, pklfile, busywindow, nothumbchanges):
    """
    ---------------------------------------------------------------------------
    [2.1] Get thumbnail images for all images in a directory.  For each image, 
    create and save a new thumb to, or load and return an existing thumb from,
    a single pickled-object file in the image folder.  Caching avoids startup
    delay for larger image folders; pickle avoids N thumb files for N images.

    Returns a list of (image-filename, PIL-thumb-image-object).  Bad file types 
    may raise IOError, or other (non-image files skipped to avoid exceptions). 
    Checks image modtime against pickled thumb modtime to see if image changed 
    since thumb created, removes orphaned thumbs for files no longer in imgdir.

    The pickled thumbs object is a single dictionary of tuples:
        {image-file-name: (image-file-modtime, thumb-file-save-bytes)}  

    Pickling PIL objects directly fails (why?), so pickles raw file-save bytes.
    It _almost_ works to pickle thumb image parts in dicts that map to keyword
    args in Image.frombytes() on reloads -- but not for GIFs only (also why?):
        save: imgdat=dict(data=imgobj.tobytes(), size=imgobj.size, mode=imgobj.mode)
        load: Image.frombytes(**pickled['imgdat'])

    The result list is derived from an os.listdir() sorted by lowercased image 
    filename to finesse both os.listdir() platform-order diffs and Python 
    dictionary random order.  Lowercase emulates Mac OS os.listdir() order.

    If no thumbs, draw a busy message on a partially built GUI window where 
    the index will be displayed (if any).  This can happen both at program 
    start or later.  Could use a popup Toplevel(), but PyPhoto has a window.
    This would ideally be threaded to avoid waits, but that's too much here.

    TBD: on errors, use an actual image file with a "?" for the placeholder?  
    This may be complex, because it must find the file in all run contexts 
    (source, app, exe, direct, PyGadgets); see windowicons.py for an example. 
        RESOLVED: this now uses an actual placeholder image file if available

    TBD: draw GUI busy message after N thumbs created, instead of 0 present?
    This might 'flash' in some contexts, but would better handle changes.

    CAVEAT: image-file changes are detected by comparing current modtimes
    to those stored in the thumbs cache.  Filesystem modtimes have well-known 
    issues which can make this test return false positives (modtime diffs). 
        RESOLVED: pass True to "nothumbchanges" to turn off this test and 
        avoid spurious regens in static archives (see 2.1 changes above).

    GOTHA: notice the "list(thumbcache.keys())" in the orphaned cleanup.
    For a dict D, using "for k in D" and "for k in D.keys()" both cause the
    del to trigger a "RuntimeError: dictionary changed size during iteration",
    despite 3.X keys view objects being advertised as auto-updated on changes.
    A "for k in D.copy()", "for k in list(D)", and "for k in list(D.keys())"
    all work (the latter form was used here because it's more explicit).
    ---------------------------------------------------------------------------
    """
    global tagwin
    global markImg # TODO HACK
    global errMarkImg # TODO HACK

    # KBR Initialize the watermark images.
    if markImg is None:
        markImg=Image.open(io.BytesIO(base64.b64decode(markbytes)))
        errMarkImg =Image.open(io.BytesIO(base64.b64decode(errMarkBytes)))

    MODTIME, FILEBYTES = 0, 1  # dicts are expensive
    thumbpath = os.path.join(imgdir, pklfile)

    # announce in GUIs
    busylabel = None
    if (busywindow and 
        (not os.path.exists(thumbpath) or os.path.getsize(thumbpath) == 0)):
        message = 'Building thumbnail images cache...'
        busylabel = Label(busywindow, text=message)
        busylabel.config(height=10, width=len(message)+10, cursor='watch')
        busylabel.pack(expand=YES, fill=BOTH)
        busywindow.lift()
        busywindow.update()

    # load existing thumbs cache
    if not os.path.exists(thumbpath):
        thumbcache = {}
    else:
        try:
            thumbfile  = open(thumbpath, 'rb')
            thumbcache = pickle.load(thumbfile)
            thumbfile.close()
        except:
            # e.g., permissions?
            # make all new in memory, and try save at end
            traceback.print_exc()  
            print('Cannot load thumbs-cache file: skipped')
            thumbcache = {}
    thumbcachechanged = False

    # remove orphaned thumbs: image deleted or renamed
    for thumbname in list(thumbcache.keys()):              # for all thumbs (keys)
        imgpath = os.path.join(imgdir, thumbname)          # img dir file
        if not os.path.exists(imgpath):
            try:
                del thumbcache[thumbname]                  # mod dict during iteration
                thumbcachechanged = True                   # write cache anew on exit
            except:
                traceback.print_exc()  
                print('Could not remove thumb:', thumbname)

    # make new thumbs: for any/all new or changed images
    thumbs = []
    sortedimgs = sortedDisplayOrder(imgdir)                   # ignore case/plat diffs
    for imgfile in sortedimgs:                                # for all files, by name
        if not isImageFileName(imgfile):                      # skip: avoid pil exception
            continue

        unsupported_formats = (".gif",".svg",".avif") # KBR currently un-tag-able image formats
        if imgfile.lower().endswith(unsupported_formats):
            continue


        # check cache+timestamps
        if ((imgfile in thumbcache) and 
            (nothumbchanges or 
               modtimeMatch(imgfile, imgdir, thumbtime=thumbcache[imgfile][MODTIME]) 
               )): 
            # use already-created thumb
            imgdat = thumbcache[imgfile][FILEBYTES]           # file-save bytes
            imgobj = Image.open(io.BytesIO(imgdat))           # pickled data => pil obj
            thumbs.append((imgfile, imgobj))                  # in py-sorted() order

            markstate = tagwin.getTags(imgfile) # load tags for cached thumb

        else:
            # new or changed: make new thumb
#            print('Making thumb for', imgfile)
            phfile  = None
            imgpath = os.path.join(imgdir, imgfile)           # open and downsize
            try:
                # [2.2] avoid Pillow too-many-open-files bug
                imgobj = openImageSafely(imgpath)

                # [2.2] reorient image to right-side up, iff needed
                imgobj = reorientImage(imgobj)

                # make thumb, changes imgobj in-place
                if hasattr(Image, 'LANCZOS'):
                    imgobj.thumbnail(size, Image.LANCZOS)     # now called this,
                else:                                         # newer Pillows only
                    imgobj.thumbnail(size, Image.ANTIALIAS)   # best downsize filter
            except:
                # on any rare exception, not always IOError
                # don't skip: make+use a placeholder instead of omitting
                traceback.print_exc()
                print('Error making thumb, trying placeholder: ', imgpath)
                phpath, phfile = findPlaceholder()
                if phpath:
                    # [2.2] avoid Pillow too-many-open-files bug
                    imgobj = openImageSafely(phpath)
                else:
                    # fallback: use a white borderless image (no name ok)
                    imgobj = Image.new(mode='1', size=size, color='#FFFFFF') 
                imgobj.thumbnail(size, Image.ANTIALIAS)

            # KBR apply a watermark image for files with tags or errors
            markstate = tagwin.getTags(imgfile)
            if markstate == 1:                # image has tags
                imgobj.paste(markImg, (5, 5))
            elif markstate == 2:              # image has tag error
                imgobj.paste(errMarkImg, (5,5))

            try:
                # add img-modtime + thumb-img-bytes to cache
                tiffs = ('.tif', '.tiff')
                extras = {} 
                if imgfile.lower().endswith(tiffs):
                    # workaround for C lib hardcrash, per [SA] note ahead
                    extras = dict(compression='raw')

                # [2.2] pass format for older pills that botch image.name
                imagename = phfile or imgfile
                imgfmt = getImageFormat(imagename)

                # direct pickles fail, so pickle file-save binary data
                imgbuf = io.BytesIO()
                imgbuf.name = imagename                     # force PIL img format?
                imgobj.save(imgbuf, imgfmt, **extras)       # save to byte buffer
                imgdat = imgbuf.getvalue()                  # saves phfile too

                modtime = os.path.getmtime(imgpath)
                thumbcache[imgfile] = (modtime, imgdat)     # pickled tuple
                thumbcachechanged = True
                thumbs.append((imgfile, imgobj))            # returned tuple
            except:
                traceback.print_exc()  
                print('Error updating cache - may remake thumb:', imgpath)

    # update pickle file if any changes
    if thumbcachechanged:
        try:
            thumbfile  = open(thumbpath, 'wb')                   # save cache dict
            thumbcache = pickle.dump(thumbcache, thumbfile)      # one big object
            thumbfile.close()                                    # shelves are complex
        except:
            # e.g., unwriteable optical disk?
            # use thumbs list in memory, rebuild on each open
            traceback.print_exc()  
            print('Cannot save thumbs-cache file: skipped')

    # the show's over...
    if busylabel:
        busylabel.destroy()

    return thumbs    # [(image-filename, PIL-thumb-image-object)]


###############################################################################
# Original thumbs-file subfolder code (supported, without newer enhancements)
###############################################################################


def isImageFileName(filename):
    """
    ---------------------------------------------------------------------------
    [SA] Detect images by filename's mimetype (not hardcoded set)
    ---------------------------------------------------------------------------
    """
    mimetype = mimetypes.guess_type(filename)[0]                    # (type?, encoding?)
    return mimetype != None and mimetype.split('/')[0] == 'image'   # e.g., 'image/jpeg'


def modtimeMatch(imgfile, imgdir, thumbdir=None, thumbtime=None, allowance=2):
    """
    ---------------------------------------------------------------------------
    [SA] Check if image file is newer than its thumb, by comparing modtimes.
    The 2-second allowance is for files on the FAT32 filesystem: see mergeall.
    Relies on copying image's modtime (stat) to thumb when thumb is created.
    Is-newer is not enough: may move in an older version of same image file.
    2.1: expanded to allow for cached modtime in new thumbs pickle file too. 
    ---------------------------------------------------------------------------
    """
    timeimg = os.path.getmtime(os.path.join(imgdir, imgfile))
    timethm = (thumbtime if thumbtime != None else 
               os.path.getmtime(os.path.join(thumbdir, imgfile)))

    return timeimg >= (timethm - allowance) and timeimg <= (timethm + allowance)


def copyModtime(imgpath, thumbpath):
    """
    ---------------------------------------------------------------------------
    [SA] Copy modtime to thumb, so comparing to image modtime detects image 
    changes.  This was lifted from mergeall, with oddities we won't redoc here.
    If the image's modtime != thumb per modtimeMatch, the image has changed.

    ----
    UPDATE: the following caution still applies to 2.0 subdir-files mode, but is
    no longer an issue for the default 2.1 pickle-file mode: 2.1 stores modtime
    in the pickle file explicitly, and image thumbs are not individual files.
    ----
    *CAUTION* Copying modtimes to thumbs can defeat timestamp-based backup 
    programs like mergeall, because changing a thumb for a new resolution 
    changes its content but not its modtime (it will be classified unchanged).

    This does not impact PyPhoto users: thumb resolution cannot be changed, 
    and thumbs are synched with images as expected.  Developers, however, 
    should take care to delete copies of a thumb folder **on all devices**
    when changing its thumbs-size and regenerating, else new thumbs may not
    be propagated to the other copies by backup programs.

    A better design would record modtimes separately from thumbs, perhaps in 
    a JSON or pickle file.  This remains a TO DO; this code today has just 1
    known user, and thumb size cannot be changed without editing code.
    ---------------------------------------------------------------------------
    """
    try:
        shutil.copystat(imgpath, thumbpath)
    except OSError as why:
        if why.errno != errno.EINVAL:       # ignore err 22 on Macs: moot
            raise                           # propagate all other errnos/excs  

# KBR embedded watermark images
errMarkBytes = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABZElEQVR4nK3VQUsUcRjH8c9/Z9V2FyvrYpBgKyYE4gvwYKdeQLc6eOzcOYLQs3jx2KWLb0LxHQjRVVKEVQixqKAtV5zpsILr+B9nwh6Ywzw/nu//9/z5MROyLMv8x6pfba1gA7s4KxhL0MZmGfAT3qODHjKECHAIf6o4THDg+7NZ6behAnf9CndSY1ulwEOcXOCnukIjtnZNGK1VcXjv0lvr3a76kyZag94wjpkqwL2cPIxVvIgOxyrn+2PlwYrAiZzcw2tM5p5ZvIwCIzkcrBRfIx5unWvXA7t0moPiz8W5wqNGnp9ovbke2MyvHI9NQE3yMBb4kpXjsWngAeLuS+7wxrG5eZU4PMUy1iLaI6z/K/AMnyP9pKAfBV7cwq+l6YKPQ0Dd7Q+lwHm8lbR3CDtCyKRHI32jCenRcP/I+72oOwiXfwFfzlf5sc1at987TTi+y8whC/vZ786r0GjjMZ5eAf4FaPxPtbny7yIAAAAASUVORK5CYII='
markbytes    = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAA+klEQVR4nO2TvUoDQRSFv50ZE4M/RZqoRcoIaycERCsJeYRASgk2imVeIW0gdUpLK0sLe/UNUmglYqeVhGXJsdhFd8C/xQhCcuA2h7nfvWeYCSSJKcpME/YnQAd94AK4BeIcrWVgGzgEdt5taVNSSZKRFPywbNpTkzRUVg7u6Z5d8fSynjteu96jGd55noEoN8iX/0gcrP4CtgJUPSeQGoriB8RzOm0MxAwuTxk97r0dPNk/INy4SXagBFRwZgtrOsBudsNzCi4iiS6gBVxjgok3ecFOKLpj4AiwQCFTXuQlkspYn2oZWPvyEv7/T5kDZxhoP/AWgcq3wFcOaWtx8MXUyQAAAABJRU5ErkJggg=='
markImg = None
errMarkImg = None


def makeThumbs_subdir(imgdir, size, subdir, busywindow):
    """
    ---------------------------------------------------------------------------
    2.0 and PP4E version (still supported for clients that require files).
    Get thumbnail images for all images in a directory.  For each image, create 
    and save a new thumb, or load and return an existing thumb.  Makes thumb  
    dir if needed.  Required to avoid startup delay for larger image folders.

    Returns a list of (image-filename, PIL-thumb-image-object).  The caller 
    can also run os.listdir on thumb dir to load.  Bad file types may raise 
    IOError, or other ([SA] non-image files now skipped to avoid exceptions). 

    Prior caveats: doesn't check file timestamps to see if image changed since 
    thumb created, doesn't cleans up thumbs imgs for files no longer in imgdir;
    ([SA] now handles both of these per below (see mergeall for timestamps)).

    [SA] If no thumbs, draw a busy message on a partially built window where 
    the index will be displayed (if any).  This can happen both at program 
    start or later.  Could use a popup Toplevel(), but PyPhoto has a window.
    This would ideally be threaded to avoid waits, but that's too much here.

    [SA] Workaround a Pillow/libtiff C lib hardcrash for tiff thumbnail saves. 
    Python dies with this message: "Assertion failed: (*pa <= 0xFFFFFFFFUL), 
    function TIFFWriteDirectoryTagSubifd, file tif_dirwrite.c, line 1869.".
    Oddly, this is not a problem when saving non-thumb tiffs via PyPhoto 'W'.

    [SA] Cleanup orphaned items in the thumbs folder that have no corresponding
    file in the images folder above (after renames and deletes), and compare 
    file timestamps to force new thumb if image has been changed (after edits). 
    *CAUTION*: see copyModtime()'s note about deleting thumbs on size changes.
    ---------------------------------------------------------------------------
    """
    thumbdir = os.path.join(imgdir, subdir)
    if not os.path.exists(thumbdir):
        os.mkdir(thumbdir)

    # [SA] announce in GUIs
    busylabel = None
    if (busywindow and 
        (not os.path.exists(thumbdir) or len(os.listdir(thumbdir)) == 0)):
        # caveat: this is redundant with 2.1 code above (factor me)
        message = 'Building thumbnail images cache...'
        busylabel = Label(busywindow, text=message)
        busylabel.config(height=10, width=len(message)+10, cursor='watch')
        busylabel.pack(expand=YES, fill=BOTH)
        busywindow.lift()
        busywindow.update()

    # [SA] remove orphaned thumbs
    for thumbfile in os.listdir(thumbdir):               # for all tumbs
        thumbpath = os.path.join(thumbdir, thumbfile)    # subdir below
        imgpath   = os.path.join(imgdir,   thumbfile)    # img dir above
        if not os.path.exists(imgpath):
            try:
                os.remove(thumbpath)
            except:
                print('Could not remove:', imgfile)

    # load or make thumbs
    thumbs = []
    for imgfile in os.listdir(imgdir):                  # for all images
        if not isImageFileName(imgfile):                # [SA] avoid exception
            continue

        thumbpath = os.path.join(thumbdir, imgfile)
        if (os.path.exists(thumbpath) and 
            modtimeMatch(imgfile, imgdir, thumbdir)):   # [SA] check timestamps
            thumbobj = Image.open(thumbpath)            # use already-created
            thumbs.append((imgfile, thumbobj))

        else:
#            print('Making thumb for', thumbpath)
            imgpath = os.path.join(imgdir, imgfile)
            try:
                imgobj = Image.open(imgpath)            # else make new thumb
                if hasattr(Image, 'LANCZOS'):                
                    imgobj.thumbnail(size, Image.LANCZOS)    # [SA] now called this
                else:                                        # newer Pillows only
                    imgobj.thumbnail(size, Image.ANTIALIAS)  # best downsize filter

                tiffs = ('.tif', '.tiff')
                if not thumbpath.lower().endswith(tiffs): 
                    imgobj.save(thumbpath)              # type via ext or passed
                else:
                    # [SA] tiff workaround for C lib hardcrash (per docstr above):
                    # skip default compression (or use format='PNG' to skip tiff); 
                    imgobj.save(thumbpath, compression='raw')

                thumbs.append((imgfile, imgobj))

            except:                                     # not always IOError
                print('Skipping image: ', imgpath)      # skip on any failure

            else:
                try:
                    copyModtime(imgpath, thumbpath)     # [SA] to detect changes
                except:
                    print('Cannot copy modtime, may remake thumb:', imgpath)

    if busylabel:
        busylabel.destroy()   # the show's over
    return thumbs


###############################################################################
# A very primitive photo viewer (see PyPhoto for much more functionality)
###############################################################################


# KBR TODO duplicated in pyphoto.py ?

class ViewOne(Toplevel):
    """
    ---------------------------------------------------------------------------
    Open a single image in a pop-up window when created.  PhotoImage
    object must be saved: images may be erased if object is reclaimed.
    ---------------------------------------------------------------------------
    """
    def __init__(self, imgdir, imgfile):
        Toplevel.__init__(self)
        self.title(imgfile)
        imgpath = os.path.join(imgdir, imgfile)
        imgobj  = PhotoImage(file=imgpath)
        Label(self, image=imgobj).pack()
        #print(imgpath, imgobj.width(), imgobj.height())   # size in pixels
        self.savephoto = imgobj                           # keep reference on me


def singleClick(self, imgdir, fileimpacted):
    #print(f"KBR: click {fileimpacted}")
    pass

# KBR TODO obsolete?

def viewer(imgdir, kind=Toplevel, cols=None):
    """
    ---------------------------------------------------------------------------
    Make thumb-links window for an image directory: one thumb button per image. 
    Use kind=Tk to show in main app window, or Frame container (pack).  imgfile
    differs per loop: must save with a default.  PhotoImage objs must be saved: 
    erased if reclaimed.  Packs row frames (versus grids, fixed-sizes, canvas). 
    ---------------------------------------------------------------------------
    """
    win = kind()
    win.title('Viewer: ' + imgdir)
    quit = Button(win, text='Quit', command=win.quit, bg='beige')   # pack first
    quit.pack(fill=X, side=BOTTOM)                                  # so clip last
    thumbs = makeThumbs(imgdir)
    if not cols:
        cols = int(math.ceil(math.sqrt(len(thumbs))))     # fixed or N x N

    savephotos = []
    while thumbs:
        thumbsrow, thumbs = thumbs[:cols], thumbs[cols:]
        row = Frame(win)
        row.pack(fill=BOTH)
        for (imgfile, imgobj) in thumbsrow:
            photo   = PhotoImage(imgobj)
            link    = Button(row, image=photo)

            handler = lambda fileImpacted=imgfile: singleClick(link, imgdir, fileImpacted)
            link.bind('<Button-1>', singleClick)
#KBR            handler = lambda savefile=imgfile: ViewOne(imgdir, savefile)
#KBR            link.config(command=handler)

            link.pack(side=LEFT, expand=YES)
            savephotos.append(photo)
    return win, savephotos


if __name__ == '__main__': 

    #--------------------------------------------------------------------------
    # A primitive viewer (see pyphoto.py for better)
    #--------------------------------------------------------------------------

    imgdir = (len(sys.argv) > 1 and sys.argv[1]) or 'images-mixed'
    main, save = viewer(imgdir, kind=Tk)
    main.mainloop()
