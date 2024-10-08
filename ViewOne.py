#!/usr/bin/env python3

# KBR 20241007 - implement as a singleton

import os,traceback,sys
from tkinter import *
from viewer_thumbs import reorientImage, openImageSafely, sortedDisplayOrder, isTaggableImage
from windowicons import trySetWindowIcon

from PIL import Image                # get image wrapper + widget
from PIL.ImageTk import PhotoImage   # replaces tkinter's version

from ObservableList import ObservableList

RunningOnMac = sys.platform.startswith('darwin')
RunningOnWindows = sys.platform.startswith('win')
RunningOnLinux = sys.platform.startswith('linux')

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
    _instance = None
    def __new__(cls, *args, **kwargs):
      if not cls._instance:
        cls._instance = super(ViewOne, cls).__new__(cls)
        cls._instance.dialog = None
      return cls._instance
      
    def __init__(self, 
                 imgdir, imgfile,           # image path+name to display
                 dirwinsize=(),             # thumbs: pass along on "D"
                 viewsize=(),               # fixed display size 
                 opener=None,               # refocus on errors?
                 nothumbchanges=False,      # thumbs: pass along on "D"
                 selList=None,
                 tagw=None,
                 appname=None):

        if self.dialog is None or not self.winfo_exists():
          Toplevel.__init__(self)
          trySetWindowIcon(self, 'icons', 'tag')   # [SA] for win+lin
          self.dialog = self.tk
          self.canvas = ScrolledCanvas(self)        # tk canvas to be reused
        else:
          self.lift()
                    
        self.appname = appname
        self.setTitle(imgfile)
        self.viewsize = viewsize                  # fixed scaling size
        self.selectionList = selList
        self.tagwin = tagw
        self.tagwin.ActiveViewOne(self) # TODO tagview uses this for next/prev
        selList.setByName(imgfile)
        
        # try to load image
        imgpath = os.path.join(imgdir, imgfile)   # img file to open
        try:
            # load img object to be reused by ops
            imgpil = openImageSafely(imgpath)     # [2.2] avoid pillow files bug
            imgpil.load()                         # [2.1] load now so errors here
            imgpil = reorientImage(imgpil)        # [2.2] right-side up, iff needed 
        except:
            # TODO this section may not work with singleton
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
        #self.canvas = ScrolledCanvas(self)        # tk canvas to be reused
        self.drawImageFirst()                     # show scaled or actual now

        # TODO most of the following section goes into the initialize-once area
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
        
        self.bind('<Destroy>', lambda event: self.cleanup())
        
        self.focus()   # on Windows, make sure new window catches events now

        # [SA] set min size as partial fix for odd window shinkage on zoomout
        # on Mac; later made mostly moot by auto-resize to screen/fixed size
        """
        self.minsize(500, 500)   # w, h
        """

    def cleanup(self):
        self.tagwin.ActiveViewOne(None) # TODO tagview uses this for next/prev
      
    def setTitle(self, imgfile):
        """
        [SA] split off from constructor for next/prior
        """
        helptxt = 'I/O=zoom, N/P=move, A/S=size, arrows=scroll'
        self.title('%s: %s (%s)' % (self.appname, imgfile, helptxt))

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
        imgfiles = list(filter(isTaggableImage, allfiles))

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
            self.selectionList.setByName(nextfile)
            #self.tagwin.showImage(nextfile) # KBR update tagview
            
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

# TODO main program for testing
