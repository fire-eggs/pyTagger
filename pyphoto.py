#!/usr/bin/env python3
"""
############################################################################
PyPhoto 2.2: a basic but open-source and portable image viewer,
with scrolling, resizing, saves, and cached thumbnails for speed.

Copyright: 2006-2018 by M. Lutz, https://learning-python.com.
License:   provided freely, but with no warranties of any kind.
Platforms: This program runs on Mac OS, Windows, and Linux
Requires:  Source-code versions (only) require Python 3.X and Pillow
Originally from the book "Programming Python, 4th Edition" by M. Lutz

Release History: 
   2.2, Sep-2018: image auto-rotation, Pillow file/format workarounds.
   2.1, Nov-2017: store a folder's thumbnails in a single pickle file.
   2.0, Sep-2017: standalone release with PyGadgets, numerous changes.
   Earlier versions appeared in the book noted above in 2010 and 2006.
     
============================================================================
OVERVIEW
============================================================================

This Python 3.X desktop-GUI program displays cached image-folder thumbnails 
which open full-size images when clicked; scrolls both images and thumbnail
displays; and provides a variety of viewing functionality.

It supports multiple image-directory thumb windows.  The initial image 
folder is either passed in via user configs, uses the "images-mixed" 
default, or is selected via a main-window button.  Later directories are 
opened by pressing "D" in either image-view or thumbnail-view windows.  

For startup speed, folder thumbnails are cached in a pickle file in 
writeable folders (subfolder caching is also coded for other programs).
The image viewer automatically resizes and scrolls images too large for 
the screen, and supports scaling to display sides and full-size views.
A limited save option also allows resized images to be saved to files.
See the in-program Help popup for more usage details. 

PyPhoto never modifies your image files in any way.  The only change it
makes to your computer is to add a single file named "_PyPhoto-thumbs.pkl"
to each folder you open in the program.  This file is the folder's 
thumbnails cache; it allows the folder to be opened quickly after its 
first open builds thumbs, and is automatically kept in synch with changes 
in the folder's images, but can be removed freely if PyPhoto is not used.

This program is still something of a placeholder for more photo editing 
ops, but it demonstrates PIL basics well enough to ship and use as is.  
For more Python photo-related tools, see the "thumbspage" web-page gallery 
generator (at learning-python.com/thumbspage.html) as well as the "tagpix" 
photo-folder organizer (at learning-python.com/tagpix.html).

============================================================================
VERSION DETAILS
============================================================================

NEW IN 2.2, Sep-2018: 

   This version was released with a new PyGadgets (all packages), to 
   incorporate two changes drawn from the thumbspage program noted above:

   1) Image auto-rotation

   Automatically rotate images and their thumbnails to display right-side 
   up, if they have "Orientation" Exif tags and tilted content.  This format
   is common for photos shot on smartphones: the natural portrait (vertical)
   device orientation yields an image tilted to the side.  Less commonly, 
   photos shot on physically tilted digital cameras may also be stored in 
   this tilted format.  Without rotation, such images would not display 
   with their top side on top in either thumbnail or full-size form, and 
   PyPhoto has no general rotate operation to manually adjust images.

   Auto-rotation is used both for thumbnails and source images, though only 
   thumbnails record rotation permanently in their files here - source images
   are rotated in memory only, and the original image file is never changed. 
   This differs from the implementation in thumbspage, which inspired the 
   auto-rotation change (learning-python.com/thumbspage.html).  Thumbspage 
   must update image files too, because the viewing browser won't rotate 
   images displayed as in-page elements; PyPhoto can rotate when viewed.

   Users of the prior version should delete their "_PyPhoto-thumbs.pkl"
   cache files in image folders to enable the auto-rotation enhancement.
   Else images will rotate when viewed, but thumbnails will remain askew.

   2) Pillow files auto-close bug workaround

   This version also adds a workaround for a Pillow (PIL) library bug, which
   could trigger too-many-open-files errors when generating many thumbnails 
   in some contexts (most commonly, Mac OS source-code usage).  The thumbspage
   program, from which this work around was borrowed, has additional notes on 
   the bug; see learning-python.com/thumbspage/viewer_thumbs.py.  

   3) Pillow buffer-file format issue workaround

   This version also codes a workaround for an obscure buffer-file format 
   issue in older Pillows, that could impact some source-code users only,
   and is not required in thumbspage; see file viewer_thumbs.py here.

NEW IN 2.1, Nov-2017: 

   This version was released with a new PyGadgets (all packages), to 
   incorporate one major change and a set of minor enhancements:

   1) Thumbnails pickle-file storage

   Store a folder's thumbnails in a single pickle file, instead of individual
   image files in a subfolder as before.  This has the same performance, but 
   avoids extra files (15k images formerly meant 15k thumbs); multiple file 
   loads and saves; and nasty modtime-copy issues for backup programs (thumbnails
   might not be backed up when their size was changed).  See viewer_thumbs.py 
   for more details.  

   Version 2.0 users: run the included delete-pyphoto2.0-thumbs-folders.py 
   Python script (or its executable), to delete all 2.0 subfolders when 
   upgrading to 2.1; else, the subfolders will be unused and wasted space.

   2) Miscellaneous enhancements
 
   Version 2.1 also now reports thumbnail-save errors in GUI popups; prints 
   all exceptions; and supports a new config-file setting to ignore image 
   modtime-based change tests during thumbnail generation where desirable
   (e.g., to accommodate modtime skew between incompatible filesystems).
   There were also other minor improvements to thumbnail processing (see
   viewer_thumbs.py for details), and images with errors are caught and 
   reported here and their thumbnails are no longer omitted in the GUI. 

NEW IN 2.0, Sep-2017 [SA]: 

   This version was released as part of PyGadgets' first standalone
   release (outside the book), along with PyCalc, PyClock, and PyToe.  
   It incorporated multiple and major extensions to boost utility:

   - New help dialog, tweak hints in window titles
   - Mac OS port: menus, reopens, focus, clicks
   - Auto-resize large images to screen size on views
   - Bind arrow keys to scroll both thumbs and images
   - Add N/P=next/prior image in folder (as displayed)
   - Add A/S=actual/scaled size (a=prior viewer sole mode)
   - Old key S (save) is now W (write)
   - Show busy message in window while creating thumbnails
   - Use LANCZOS resize filter in all resize contexts in newer Pillows:
     now the best quality (if slowest) for both shrinking and expanding:
     pillow.readthedocs.io/en/4.2.x/handbook/concepts.html#concept-filters
   - Move window to upper-left corner if too large for display or partially 
     off-screen, but do not center if smaller than display (a user choice)
   - Get screen max size reliably (this is a bit loose in Tk)
   - Implement ViewSize fixed-size option for image views and scaling
   - Workaround a C libs hardcrash for tiff thumbnail saves: no compress

   PyPhoto is still a bit primitive, and something of a PIL demo
   (e.g. images are not resized on window resizes, and there is no 
   cropping, etc.), but is also illustrative of general PIL use.

Older versions appeared as examples in the book "Programming Python."
The current PyPhoto derives from the original in 2010's 4th Edition.

NEW IN 1.1, 2010, PP4E
   Updated to run in Python 3.1 and latest PIL.

NEW IN 1.0, 2006, PP3E
   Now does two flavors of resizing: the image is resized to one of the 
   display's dimensions if clicked, and zoomed in or out in 10% increments 
   on key presses; generalize me.  Caveat: images seem to lose quality
   and/or pixels after many resizes (this is probably a limitation of PIL).

============================================================================
SCALING NOTES
============================================================================

The following scaler adapted from PIL's thumbnail code is similar to the
screen height scaler here, but only shrinks:

    x, y = imgwide, imghigh
    if x > scrwide: y = max(y * scrwide // x, 1); x = scrwide
    if y > scrhigh: x = max(x * scrhigh // y, 1); y = scrhigh

The related thumbspage program (at learning-python.com/thumbspage.html) 
uses an alternative display-fit scaling method which might work here too;
it's coded and run in JavaScript:

    // per smallest-fit side 
    ratio = Math.min(displayWidth / trueWidth, displayHeight / trueHeight);

    if (! stretchBeyondActual) {
        ratio = Math.min(ratio, 1.0);    // don't expand beyond actual size
    }
    return {width:  (trueWidth  * ratio), 
            height: (trueHeight * ratio)};

============================================================================
CAVEATS/TBDS
============================================================================

1) TIFF drawing quality on Mac OS El Capitan

On test and development machines, TIFF images and their thumbnails 
render poorly (with artifacts) in Mac OS apps and source-code on 
El Capitan, but accurately on Mac OS Sierra in all modes (and always
flawlessly on Windows and Linux).  This may indicate a newer shared 
libtiff on Sierra, which might be fixed by installs on El Capitan.

2) Image-save limitations

Saves ("W") work well in typical roles, but are not always as simple 
as giving a ".xxx" filename extension (e.g., this may discard GIF 
transparencies), and some image-type saves may not work at all due 
to the Pillow library's constraints, especially for conversions 
(e.g., they may leave zero-length files).  To be improved if usage
warrants.  Version 2.1 at least adds a GUI popup on save errors.

3) Image auto-placement is one-sided

The automatic move-to-upper-left-corner works only when the image 
is off-screen to the right, not left; this could be generalized
to work on either screen side, but that seems a bit superfluous.

4) Mac OS screenshot shadows on Mac OS El Capitan

The default shadows that Mac OS adds around its screenshots sometimes
render as all-black in Pillow images and thumbnails as they're used here.
Oddly, this has been observed ONLY on a Mac OS El Capitan machine; it 
does not occur on a Mac OS Sierra machine, and Windows and Linux seem 
to always render the shadow properly too.  Hence, this appears to be
Mac-only, and specific to either Mac OS version or a single machine.
(See also #1 above: El Capitan's image-drawing stack seems flaky.)

If not, this may be prohibitively complex.  A magic-but-sadly-undocumented 
Pillow remedy seems unlikely, and removing shadows manually seems absurd:
   https://stackoverflow.com/questions/18293290/
      programmatically-remove-apple-screen-capture-shadow-borders 

5) And so on (this project is open ended, and awaits user feedback)

Other TBDs include: 
- Rearrange thumbnails when window resized, based on current window size? 
- [DONE] Resize images to fit display/window size when first opened?
- Avoid scrolls if image size is less than window max size (e.g., use 
  a simple Label if imgwide <= scrwide and imghigh <= scrhigh)? 
- Better fit scaled images to display (it's not a 100% match everywhere)?
- Add filename labels to the thumbs window (as it, it's like a proof sheet)?
- Image cropping, annotation, drawing, ... (this gets silly at some point)?

############################################################################
"""

import sys, math, os, traceback
from tkinter import *
from tkinter.filedialog import SaveAs, Directory, askdirectory
from tkinter.messagebox import showerror

from TagView import *
tagwin = None

# [SA] require PIL/Pillow install
pillowerror = """
Pillow 3rd-party package is not installed.
...This package is required by PyPhoto for both thumbnails generation
...and image file types not supported by Pythons without Pillow.  Any 
...Python supports GIFs, and Pythons using Tk 8.6 or later add PNGs, but 
...thumbnails expect Pillow.  See https://pypi.python.org/pypi/Pillow.
"""

try:
    from PIL import Image                # get image wrapper + widget
    from PIL.ImageTk import PhotoImage   # replaces tkinter's version
except ImportError:
    print(pillowerror)
    sys.exit(0)
    # don't continue: some image types may load, but need PIL to make thumbnails
    # Pillow install required for source-code only: apps/exes have PIL "baked in"

# thumbnail generation code, developed earlier in book
from viewer_thumbs import makeThumbs, isImageFileName, sortedDisplayOrder

# [2.2] auto-rotation of tilted images, avoid Pillow too-many-open-files bug
from viewer_thumbs import reorientImage, openImageSafely

# [SA] Mac port (and other backports)
RunningOnMac = sys.platform.startswith('darwin')
RunningOnWindows = sys.platform.startswith('win')
RunningOnLinux = sys.platform.startswith('linux')

# [SA]: set window icons on Windows and Linux
from windowicons import trySetWindowIcon

# remember last dirs across all windows
saveDialog = SaveAs(title='Save As (filename extension gives image type)')
if RunningOnMac:
    openargs = dict(message='Select Image Directory To Open')   # [SA]
else:
    openargs = dict(title='Select Image Directory To Open')
openDialog = Directory(**openargs)

trace = print  # or lambda *x: None
appname = 'PyPhoto 2.2'


############################################################################
# Canvas with dual scroll bars, used by both thumbnail and image windows
############################################################################

class ScrolledCanvas(Canvas):
    """
    a canvas in a container that automatically makes
    vertical and horizontal scroll bars for itself
    """
    def __init__(self, container):
        Canvas.__init__(self, container)
        self.config(borderwidth=0)
        vbar = Scrollbar(container)
        hbar = Scrollbar(container, orient='horizontal')

        vbar.pack(side=RIGHT,  fill=Y)                 # pack canvas after bars
        hbar.pack(side=BOTTOM, fill=X)                 # so clipped first
        self.pack(side=TOP, fill=BOTH, expand=YES)

        vbar.config(command=self.yview)                # call on scroll move
        hbar.config(command=self.xview)
        self.config(yscrollcommand=vbar.set)           # call on canvas move
        self.config(xscrollcommand=hbar.set)


############################################################################
# View a single image selected in thumbnails window
############################################################################

class ViewOne(Toplevel):
    """
    --------------------------------------------------------------
    A pop-up window that opens a single image when created.
    Scrollable vertically and horizontally if too big for display.

    This was initially coded as a class because PhotoImage objects 
    must be saved, else images may be erased from GUI if reclaimed.

    On mouse clicks, resizes to display's height or width, either
    stretching or shrinking.  On I/O keypress, zooms image in/out.
    Both resizing schemes maintain the original aspect ratio; its
    code is factored to avoid redundancy here as possible.

    [SA] See 2.0 changes list in main docstring for updates:
    there were too many extensions to list here.

    [2.1] Catch and report exceptions for images with errors,
    whose thumbnails are no longer omitted in 2.1.  Pillow uses 
    a "lazy" model in which open() just identifies the file, but
    the complete load() is deferred until later processing.  This 
    can be a major problem, as exceptions might occur anywhere and
    anytime for images with errors.  Here, and on next/prior image,
    call load() explicitly to force errors to happen immediately.
    --------------------------------------------------------------
    """
    def __init__(self, 
                 imgdir, imgfile,           # image path+name to display
                 dirwinsize=(),             # thumbs: pass along on "D"
                 viewsize=(),               # fixed display size 
                 opener=None,               # refocus on errors?
                 nothumbchanges=False):     # thumbs: pass along on "D"

        Toplevel.__init__(self)
        self.setTitle(imgfile)
        trySetWindowIcon(self, 'icons', 'pygadgets')   # [SA] for win+lin
        self.viewsize = viewsize                  # fixed scaling size

        # try to load image
        imgpath = os.path.join(imgdir, imgfile)   # img file to open
        try:
            # load img object to be reused by ops
            imgpil = openImageSafely(imgpath)     # [2.2] avoid pillow files bug
            imgpil.load()                         # [2.1] load now so errors here
            imgpil = reorientImage(imgpil)        # [2.2] right-side up, iff needed 
        except:
            # [2.1] can fail on OSError+ in Pillow
            traceback.print_exc()
            self.destroy()
            showerror('PyPhoto: Image Load',
                      'Cannot load image file:\n%s' % imgpath)
            if opener: 
                opener.focus_force()              # abandon after error popup
                if RunningOnLinux: opener.lift()  # else root win stays above
            return                                # abandon after error popup

        self.trueimage = imgpil                   # for all ops till N/P
        self.canvas = ScrolledCanvas(self)        # tk canvas to be reused
        self.drawImageFirst()                     # show scaled or actual now

        # bind keys/events for this image-view window

        self.canvas.bind('<Button-1>', self.onSizeToDisplayHeight)
        self.canvas.bind('<Button-3>', self.onSizeToDisplayWidth)
        if RunningOnMac:
            self.canvas.bind('<Button-2>',  self.onSizeToDisplayWidth)   # [SA]
            self.bind('<Control-Button-1>', self.onSizeToDisplayWidth)

        self.bind('<KeyPress-i>', self.onZoomIn)
        self.bind('<KeyPress-o>', self.onZoomOut)
        self.bind('<KeyPress-w>', self.onSaveImage)
        self.bind('<KeyPress-d>', 
            lambda event: onDirectoryOpen(self, dirwinsize, viewsize, nothumbchanges))

        # [SA] question=? but portable, help key in all gadgets
        self.bind('<KeyPress-question>', lambda event: onHelp(self))
 
        # [SA] bind arrow keys to scroll canvas too (tbd: increment?)
        self.bind('<Up>',    lambda event: self.canvas.yview_scroll(-1, 'units'))
        self.bind('<Down>',  lambda event: self.canvas.yview_scroll(+1, 'units'))
        self.bind('<Left>',  lambda event: self.canvas.xview_scroll(-1, 'units'))
        self.bind('<Right>', lambda event: self.canvas.xview_scroll(+1, 'units'))

        # [SA] add next/prior image in this image's folder
        self.bind('<KeyPress-n>', self.onNextImage)
        self.bind('<KeyPress-p>', self.onPrevImage)
        self.imgdir, self.imgfile, self.dirwinsize = imgdir, imgfile, dirwinsize

        # [SA] add actual/scaled size (actual=former version's only mode)
        self.bind('<KeyPress-a>', lambda event: self.drawImageSized(self.trueimage))
        self.bind('<KeyPress-s>', lambda event: self.drawImageFirst())

        self.focus()   # on Windows, make sure new window catches events now

        # [SA] set min size as partial fix for odd window shinkage on zoomout
        # on Mac; later made mostly moot by auto-resize to screen/fixed size
        """
        self.minsize(500, 500)   # w, h
        """

    def setTitle(self, imgfile):
        """
        [SA] split off from constructor for next/prior
        """
        helptxt = 'I/O=zoom, N/P=move, A/S=size, arrows=scroll'
        self.title('%s: %s (%s)' % (appname, imgfile, helptxt))

    def getMaxSize(self, constrained=True):
        """
        [SA] fullscreen (W, H) size, factored to common code;
        viewsize is experimental, but suffices to limit scaling max; 
        oddness: Tk's self.maxsize() height varies across calls, and
        on Mac is < self.winfo_screenwidth()/.winfo_screenheight();
        """
        #trace('==>', self.maxsize())
        #trace('==>', (self.winfo_screenwidth(), self.winfo_screenheight()))

        scrwide, scrhigh = self.winfo_screenwidth(), self.winfo_screenheight()
        if not constrained:
            return (scrwide, scrhigh)                    # wm screen size (x,y)
        else:
            return self.viewsize or (scrwide, scrhigh)   # user limit, or wm

    #
    # Drawing
    #

    def drawImageFirst(self):
        """
        [SA] draw from self.trueimage, ether scaled or actual;
        called on first open, next/prior, and S=scale key, but 
        trueimage is set by the first two of these only, and is
        used by most ops (viewimage is used by zooms and saves);

        resize large images to screen or fixed size initially;
        smaller images are still drawn by actual size, as before;
        viewsize is still experimental (scaling to screen size in
        onSizeToDisplayBoth is better), but suffices to limit max;

        [SA] imgpil.width and imgpil.height are not available in 
        earlier Pillows: use the older .size tuple-pair instead;
        """
        imgpil = self.trueimage
        imgwide, imghigh = imgpil.size                   # size in pixels (x,y)
        scrwide, scrhigh = self.getMaxSize()             # wm screen size (x,y)

        if imgwide <= scrwide and imghigh <= scrhigh:    # too big for display?
            self.drawImageSized(imgpil)                  # no:  win size per img
        else:                                            # yes: resize to screen
            self.onSizeToDisplayBoth()                   # scale to screen W and H
 
        """
        # this else was not as good...
        diffwide = imgwide - scrwide                 # use most-exceeded edge
        diffhigh = imghigh - scrhigh   
        if diffwide > diffhigh:                      # either may be negative
            self.onSizeToDisplayWidth(event=None)    
        else:
            self.onSizeToDisplayHeight(event=None)
        """

    def drawImageSized(self, imgpil):
        """
        draw imgpil, as it is sized, in current window/canvas;
        imgpil may be the original actual size, or a temp resize;
        """
        imgtk    = PhotoImage(image=imgpil)              # not file=imgpath
        imgwide  = imgtk.width()                         # size in pixels
        imghigh  = imgtk.height()                        # same as imgpil.size
        scrwide, scrhigh = self.getMaxSize()             # wm screen size (x,y)
        
        fullsize = (0, 0, imgwide, imghigh)              # scrollable
        viewwide = min(imgwide, scrwide)                 # viewable
        viewhigh = min(imghigh, scrhigh)

        canvas = self.canvas
        canvas.delete('all')                             # clear prior photo
        canvas.config(height=viewhigh, width=viewwide)   # viewable window size
        canvas.config(scrollregion=fullsize)             # scrollable area size
        canvas.create_image(0, 0, image=imgtk, anchor=NW)

        self.savephoto = imgtk                           # keep reference on me
        self.viewimage = imgpil                          # currently shown size
#        trace((scrwide, scrhigh), imgpil.size)

        # [SA] move to upper-left if too big or partially off-screen
        self.update()
        coords = self.geometry()                         # e.g., '721x546+521+23'
        wmsizeX, wmsizeY = \
            [int(x) for x in coords.split('+')[0].split('x')]
        upleftX, upleftY = \
            [int(x) for x in coords.split('+')[1:3]]
        truewide, truehigh = self.getMaxSize(constrained=False)
        if (upleftX + wmsizeX > truewide) or (upleftY + wmsizeY > truehigh):
            self.geometry('+0+0')
        #trace((upleftX, wmsizeX, truewide), (upleftY, wmsizeY, truehigh))

        # [SA] the point of this seems lost in translation...
        """
        if imgwide <= scrwide and imghigh <= scrhigh:    # too big for display?
            self.state('normal')                         # no: win size per img
        elif sys.platform[:3] == 'win':                  # do windows fullscreen
            self.state('zoomed')                         # others use geometry()
        else:                                            # [SA] Mac is different...
            win.wm_attributes('-fullscreen', 1)
        """

    #
    # Scaling
    #

    def sizeToDisplaySide(self, scaler):
        """
        resize to fill one side (or both) of the display;
        [SA] start from self.trueimage, not last view size;
        [SA] lanczos filter not available in earlier Pillows;
        """
        imgpil = self.trueimage                           # scale from full size
        imgwide, imghigh = imgpil.size                    # img size in pixels
        scrwide, scrhigh = self.getMaxSize()              # wm screen size (x,y)
        newwide, newhigh = scaler(scrwide, scrhigh, imgwide, imghigh)
        if hasattr(Image, 'LANCZOS'):
            filter = Image.LANCZOS    # [SA] best for all, if available
        else:
            if (newwide * newhigh < imgwide * imghigh):
                filter = Image.ANTIALIAS                      # shrink: antialias
            else:                                             # grow: bicub sharper
                filter = Image.BICUBIC
        newimg = imgpil.resize((newwide, newhigh), filter)
        self.drawImageSized(newimg)

    def onSizeToDisplayHeight(self, event):
        def scaleHigh(scrwide, scrhigh, imgwide, imghigh):
            newwide = int(imgwide * (scrhigh / imghigh))        # 3.x true div
            newhigh = scrhigh                                   # [SA] -border
            return (newwide, newhigh)                           # proportional
        self.sizeToDisplaySide(scaleHigh)

    def onSizeToDisplayWidth(self, event):
        def scaleWide(scrwide, scrhigh, imgwide, imghigh):
            newhigh = int(imghigh * (scrwide / imgwide))        # 3.x true div
            newwide = scrwide                                   # [SA] -border
            return (newwide, newhigh)
        self.sizeToDisplaySide(scaleWide)

    def onSizeToDisplayBoth(self):
        """
        [SA] scale to fit both height and width of screen;
        the 90% scale-down is meant allow for window borders:
        should this happen in sizeToDisplaySide for all (tbd)?
        """
        def scaleBoth(scrwide, scrhigh, imgwide, imghigh):
            scrwide, scrhigh = (int(x * .90) for x in (scrwide, scrhigh))
            newwide, newhigh = imgwide, imghigh
            if imgwide > scrwide:
                newhigh = int(imghigh * (scrwide / imgwide))        
                newwide = scrwide 
            if imghigh > scrhigh:
                newwide = int(imgwide * (scrhigh / imghigh))
                newhigh = scrhigh    
            return (newwide, newhigh)
        self.sizeToDisplaySide(scaleBoth)

    #
    # Zooming
    #

    def zoom(self, factor):
        """
        zoom in or out in increments;
        [SA] must use viewimage here, else not cumulative;
        [SA] lanczos filter not available in earlier Pillows;
        """
        imgpil = self.viewimage              # zoom from last display size
        wide, high = imgpil.size             # may be scaled, actual, zoomed
        if hasattr(Image, 'LANCZOS'):
            filter = Image.LANCZOS           # [SA] best for all, if available
        else:
            if factor < 1.0:                 # antialias best if shrink
                filter = Image.ANTIALIAS     # also nearest, bilinear
            else:
                filter = Image.BICUBIC
        newimg = imgpil.resize((int(wide * factor), int(high * factor)), filter)
        self.drawImageSized(newimg)

    def onZoomIn(self, event, incr=.10):
        self.zoom(1.0 + incr)

    def onZoomOut(self, event, decr=.10):
        self.zoom(1.0 - decr)

    #
    # Saving
    #

    def onSaveImage(self, event):
        """
        save current image size/state to a file;
        per PIL, fiename extension gives image type;
        [SA] save from viewimage: currently shown size;
        [SA] set initialfile name for convenience;
        [2.1] catch/report save errors, console+GUI
        """
        filename = saveDialog.show(initialfile=self.imgfile)
        if filename:
            try:
                self.viewimage.save(filename)
            except:
                traceback.print_exc()
                print('Error saving image file: not saved') 
                showerror('PyPhoto: Image Save',
                      'Cannot save image file:\n%s' % filename)
        self.focus_force()   # [SA] for Mac

    #
    # Navigating
    #

    def switchimage(self, ixmod):
        """
        [SA] add next/prior image in this image's folder;
        redraws in same window/canvas, to avoid flicker if 
        draw in a new window and erase the old one (and the 
        "ViewOne" class name now really means one at a time);

        [2.1] catch/report images with errors (whose thumbs 
        are no longer omitted); error imgs stop the next/prior 
        progression: users must click a new thumb past it;

        [2.1] must call viewer_thumb's sortedDisplayOrder(),
        not os.listdir() directly, so the next/prior order
        implemented here matches thumbs-display order;
        """
        currdir, currfile = self.imgdir, self.imgfile
        allfiles = sortedDisplayOrder(currdir)
        imgfiles = list(filter(isImageFileName, allfiles))

        currix = imgfiles.index(currfile)
        newix  = currix + ixmod
        newix  = len(imgfiles)-1 if newix < 0 else newix % len(imgfiles)
        nextfile = imgfiles[newix]   # wrapped around

        imgpath = os.path.join(currdir, nextfile)     # img file to open
        try:
            # open image object to be reused
            nextimgpil = openImageSafely(imgpath)     # [2.2] avoid Pillow files bug
            nextimgpil.load()                         # [2.1] load now so errors here
            nextimgpil = reorientImage(nextimgpil)    # [2.2] right-side up, iff needed 
        except:
            # [2.1] can fail on OSError+ in Pillow
            traceback.print_exc()
            showerror('PyPhoto: Image Load',
                      'Cannot load image file:\n%s' % imgpath)
            self.focus_force()
            if RunningOnLinux: self.lift()            # else root stays above
        else:
            # move iff image loaded
            self.imgfile = nextfile
            self.setTitle(nextfile)
            self.trueimage = nextimgpil               # save for ops on image
            self.drawImageFirst()                     # new image, same win/canvas
            tagwin.showImage(nextfile) # KBR update tagview
            
        """
        # or new window: this worked but was too twitchy...
        ViewOne(currdir, nextfile, self.dirwinsize, (plus new stuff))
        self.destroy()
        """

    def onNextImage(self, event):
        self.switchimage(+1)

    def onPrevImage(self, event):
        self.switchimage(-1)

# End class ViewOne

canvas = None # TODO HACK
btnSelected = None # TODO HACK

def singleClick(btn, imgdir, fileimpacted):
    """
    Single mouse click handling (selection). 
    
    Currently single-selection only.
    """
    global canvas # TODO HACK
    global tagwin # TODO HACK
    global btnSelected # TODO HACK
    
    orig_color = btn.cget("background")
    
    # Revert any previously selected thumbnail.
    if btnSelected is not None:
        btnSelected.config(bg=orig_color, activebackground=orig_color)  
      
    #print(f"KBR: click2 {btn} {imgdir} {fileimpacted}")
    btnSelected = btn
    btn.configure(relief='sunken') # TODO needs more obvious indication
    btn.configure(bg='red',activebackground='red')
    
    canvas.update()
    
    tagwin.showImage(fileimpacted) # Notify tag window
    
    # TODO not updating until mouse move: why?
  

############################################################################
# View the thumbnails window for an initial or chosen directory
############################################################################

def viewThumbs(imgdir,                         # open this folder
               kind=Toplevel,                  # thumbs window: Tk or Toplevel 
               dirwinsize=(),                  # size of this thumbs window
               viewsize=(),                    # size of each image-view window
               numcols=None,                   # fixed, else per #thumbnails 
               nothumbchanges=False):          # don't detect image changes?
    """
    --------------------------------------------------------------
    Make main (Tk) or pop-up (Toplevel) thumbnail-buttons window.
    Uses fixed-size buttons, and a bi-scrollable canvas.

    Sets scrollable (full) size of canvas, and places thumbs 
    at absoute x,y coordinates in the canvas.

    No longer assumes that all thumbs are the same size:
    uses max of all (x,y) for all, as some may be smaller.

    [SA] See 2.0 changes list in main docstring for updates:
    there were too many extensions to list here.

    CAUTION: changing thumb size can defeat backup programs; 
    delete all thumbs on size changes (see viewer_thumbs.py).
    --------------------------------------------------------------
    """
    global canvas # TODO HACK

    global tagwin # TODO HACK
    
        
    win = kind()
    helptxt = 'D=open'
    win.title('%s: %s (%s)' % (appname, imgdir, helptxt))
    trySetWindowIcon(win, 'icons', 'pygadgets')   # [SA] for win+lin

    # [SA] add new Help button
    # [SA] Quit=destroy (this window only unless last Tk), not quit (entire app)
    tools = Frame(win, bg='beige')
    tools.pack(side=BOTTOM, fill=X)
    quit = Button(tools, text=' Quit ', command=lambda: onQuit(win)) # KBR command=win.destroy)   # [SA] no bg= on Mac
    quit.pack(side=RIGHT, expand=YES)
    help = Button(tools, text=' Help ', command=lambda: onHelp(win))
    help.pack(side=LEFT, expand=YES)

    # [SA] question=? but portable, help key in all gadgets
    win.bind('<KeyPress-question>', lambda event: onHelp(win))

    tagwin=TagView(imgdir)
    tagwin.initScan()

    # make or load thumbs ==> [(imgfile, imgobj)]
    TSIZE = 160
    thumbs = makeThumbs(imgdir,                             # all images in folder
                        size=(TSIZE, TSIZE),                    # fixed thumbnails size
#KBR                        size=(128, 128),                    # fixed thumbnails size
                        busywindow=win,                     # announce in GUI
                        nothumbchanges=nothumbchanges,      # don't detect changes? 
                        _tagswin=tagwin)
                        
    tagwin.doneScan()
    
    numthumbs = len(thumbs)
#KBR    
#    if numthumbs == 0:                                      # no-image dir?
#        numcols = numrows = 0                               # [SA] avoid / 0 exc
#    else:
#        if not numcols:
#            numcols = int(math.ceil(math.sqrt(numthumbs)))  # fixed or N x N
#        numrows = int(math.ceil(numthumbs / numcols))       # 3.x true div

    #print(f"KBR:{dirwinsize}")

    width, height = dirwinsize                      # [SA] new configs model
    canvas = ScrolledCanvas(win)                    # init viewable window size
    canvas.config(height=height, width=width)       # changes if user resizes

    if numthumbs == 0:                                      # no-image dir?
        numcols = numrows = 0                               # [SA] avoid / 0 exc
    else:
        if not numcols:
            numcols = int(width / TSIZE) # TODO KBR magic number see above
        numrows = int(math.ceil(numthumbs / numcols))       # 3.x true div


    # max w|h: thumb=(name, obj), obj.size=(width, height)
    if numthumbs == 0:
        linksize = 0   # [SA] avoid empty-seq max() exc
    else:
        linksize = max(max(thumb[1].size) for thumb in thumbs)
#    trace(linksize)
    fullsize = (0, 0,                                   # upper left  X,Y
        (linksize * numcols), (linksize * numrows) )    # lower right X,Y
    canvas.config(scrollregion=fullsize)                # scrollable area size

    rowpos = 0
    savephotos = []
    allbtns = []
    while thumbs:
        thumbsrow, thumbs = thumbs[:numcols], thumbs[numcols:]
        colpos = 0
        for (imgfile, imgobj) in thumbsrow:
            photo = PhotoImage(imgobj)
            link  = Button(canvas, image=photo, relief="raised")
            allbtns.append(link) # keep reference to avoid gc
            #if imgfile == '2009-VaioP.jpg':
            #  print(f"{link} {imgfile}")
            
            def handler1(event, _link=link, _imgfile=imgfile):
              #print(f"{_link} {_imgfile}")
              singleClick(_link, imgdir, _imgfile)
            link.bind('<Button-1>', handler1)

            def handler2(event, _imgfile=imgfile):
              ViewOne(imgdir, _imgfile, dirwinsize, viewsize, win, nothumbchanges)
            link.bind('<Double-1>', handler2)
            
#            def handler(_imgfile=imgfile): 
#                ViewOne(imgdir, _imgfile, dirwinsize, viewsize, win, nothumbchanges)
#            link.config(command=handler, width=linksize, height=linksize)

            link.pack(side=LEFT, expand=YES)
            canvas.create_window(colpos, rowpos, anchor=NW,
                    window=link, width=linksize, height=linksize)
            colpos += linksize
            savephotos.append(photo)
        rowpos += linksize

    win.savephotos = savephotos   # keep references to all to avoid gc

    # bind keys/events for this directory-view window
    win.bind('<KeyPress-d>', 
        lambda event: onDirectoryOpen(win, dirwinsize, viewsize, nothumbchanges))

    # [SA] bind arrow keys to scroll canvas too (tbd: increment?)
    win.bind('<Up>',    lambda event: canvas.yview_scroll(-1, 'units'))
    win.bind('<Down>',  lambda event: canvas.yview_scroll(+1, 'units'))
    win.bind('<Left>',  lambda event: canvas.xview_scroll(-1, 'units'))
    win.bind('<Right>', lambda event: canvas.xview_scroll(+1, 'units'))
    
    win.bind('<Destroy>', cleanup)
    
    win.focus()   # [SA] on Windows, make sure new window catches events now
    return win


############################################################################
# Utilities, having multiple class and non-class clients
############################################################################


def onDirectoryOpen(parentwin, dirwinsize, viewsize, nothumbchanges):
    """
    open a new image directory in a new main window;
    available via "D" in both thumb and img windows
    """
    dirname = askdirectory(parent=parentwin,mustexist=True)
    #dirname = openDialog.show()
    if dirname:
        viewThumbs(dirname, Toplevel, dirwinsize, viewsize, 
                   nothumbchanges=nothumbchanges)
    else:
        parentwin.focus_force()   # [SA] for Mac

def cleanup(*args):
    global tagwin
    if tagwin is not None:
        tagwin.destroy()
        tagwin = None
    
def onQuit(parentwin):
    global tagwin
    if tagwin is not None:
        tagwin.destroy()
        tagwin = None
    parentwin.destroy()

def onHelp(parentwin):
    """
    [SA] new help dialog - simple but sufficient;
    used for 'help' button click, '?' keyboard press, Mac menus;
    '?' keypress and Mac menus work in both thumb and image windows;
    """
    from helpmessage import showhelp
    showhelp(parentwin, 'PyPhoto', HelpText, forcetext=False,
             setwinicon=lambda win:
                    trySetWindowIcon(win, 'icons', 'pygadgets'))
    #parentwin.focus_force()   # now done in helpmessage


HelpText = ('PyPhoto 2.2\n'
            '\n'
            'A Python/tkinter/PIL image-viewer GUI.\n'
            'For Mac OS, Windows, and Linux.\n'
            'From the book Programming Python.\n'
            'Author and © M. Lutz 2006-2018.\n'
            '\n'
            'In directory windows:\n'
            '▶ Key D opens another image directory\n'
            '▶ Clicking an image\'s thumbnail opens it in an '
            'image-view window at scaled size\n'
            '\n'
            'In image-view windows:\n'
            '▶ Key D opens another image directory\n'
            '▶ Keys N/P open the next/prior image\n'
            '▶ Keys I/O zoom the image in/out\n'
            '▶ Keys A/S show actual/scaled size\n'
            '▶ Key W saves (writes) the current image\n'
            '▶ Leftclick and rightclick resize to screen height '
            'and width, respectively (on Macs, rightclick=two-finger '
            'click or control+click)\n'
            '\n'
            'In both window types, key ?=Help, and the Up/Down '
            'and Left/Right arrow keys scroll vertically and '
            'horizontally, respectively.\n'
            '\n'
            'For W saves, the filename\'s ".xxx" extension gives its '
            'image type.  For example, to both shrink a PNG and convert '
            'it to GIF, zoom out with O and save as ".gif" with W.\n'
            '\n'
            'A "_PyPhoto-thumbs.pkl" file is created in each opened image '
            'folder when possible, to store image thumbnails for fast access.  '
            'Its thumbs are kept in sync with images.\n'
            '\n'
            'PyPhoto source-code distributions (but not apps or '
            'executables) require installation of the Pillow extension '
            'package from https://pypi.python.org/pypi/Pillow.\n'
            '\n'
            'For downloads and more apps, visit:\n'
            'http://learning-python.com/programs.html'
           )


############################################################################
# Top-level logic: get configs, get first folder, display thumbnails
############################################################################

if __name__ == '__main__':
    """
    open dir = default or cmdline arg
    else show simple window to select
    """ 
    from getConfigs import getConfigs               # [SA] new gadgets utility
    #KBR defaults = dict(InitialSize='500x400',          # size of dir/thumbs window
    defaults = dict(InitialSize='1500x900',          # size of dir/thumbs window
                    InitialFolder='images-mixed',   # None = ask for dir
                    ViewSize=None,                  # None = scale to screen
                    NoThumbChanges=False)           # True = skip change detection [2.1]
    configs = getConfigs('PyPhoto', defaults)       # load from file or args

    imgdir     = configs.InitialFolder
    dirwinsize = configs.InitialSize.split('x')            # 'WidthxHeight'
    dirwinsize = [int(x) for x in dirwinsize]              # (Width, Height)
    viewsize   = configs.ViewSize
    viewsize   = viewsize.split('x') if viewsize else ()   # e.g., '800x600'
    viewsize   = list(map(int, viewsize))                  # (800, 600)
    nothumbchanges = configs.NoThumbChanges

    if imgdir and os.path.exists(imgdir):
        mainwin = viewThumbs(imgdir, Tk, dirwinsize, viewsize, 
                             nothumbchanges=nothumbchanges)
    else:
        mainwin = Tk()
        mainwin.geometry('250x50') 
        mainwin.title(appname + 'Open')
        handler = lambda: onDirectoryOpen(mainwin, dirwinsize, viewsize, nothumbchanges)
        Button(mainwin, text='Open Image Directory', 
               command=handler).pack(expand=YES, fill=BOTH)
        trySetWindowIcon(mainwin, 'icons', 'pygadgets')   # [SA] for win+lin

    if RunningOnMac:
        # Mac requires menus, deiconifies, focus

        # [SA] on Mac, customize app-wide automatic top-of-display menu
        from guimaker_pp4e import fixAppleMenuBar
        fixAppleMenuBar(window=mainwin,
                        appname='PyPhoto',
                        helpaction=lambda: onHelp(mainwin),
                        aboutaction=None,
                        quitaction=mainwin.quit)    # immediate, bound method

        # [SA] reopen auto on dock/app click and fix tk focus loss on deiconify
        def onReopen():
            mainwin.lift()
            mainwin.update()
            temp = Toplevel()
            temp.lower()
            temp.destroy()
        mainwin.createcommand('::tk::mac::ReopenApplication', onReopen)

    mainwin.mainloop()
