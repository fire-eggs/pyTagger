#!/usr/bin/env python3

# TODO remember window size/position [is this per-directory?]
# TODO thumbnail size changeable
# TODO how to update 'T' marker when tagged status changes?
# TODO how to add taggability for GIF?
# TODO create my own icon to replace pygadgets.gif
# TODO what's that fancier/themable tkinter extension?
# TODO quit/close consistancy (only the first window's quit button actually shuts down)
# TODO two copies of scrolledcanvas?
# TODO two copies of ViewOne?
# TODO canvas resize: want to show the "current" thumbs (e.g. filtered) not necessarily all
# TODO canvas resize should do nothing if numcols doesn't change
# TODO when image removed from selection, need to rebuild common tags list

import sys, math, os, traceback
from tkinter import *
from tkinter.filedialog import SaveAs, Directory, askdirectory
from tkinter.messagebox import showerror

try:
    from PIL import Image                # get image wrapper + widget
    from PIL.ImageTk import PhotoImage   # replaces tkinter's version
except ImportError:
    print("""
Pillow 3rd-party package is not installed.
...This package is required by PyPhoto for both thumbnails generation
...and image file types not supported by Pythons without Pillow.  Any 
...Python supports GIFs, and Pythons using Tk 8.6 or later add PNGs, but 
...thumbnails expect Pillow.  See https://pypi.python.org/pypi/Pillow.
""")
    sys.exit(0)
    # don't continue: some image types may load, but need PIL to make thumbnails
    # Pillow install required for source-code only: apps/exes have PIL "baked in"

from TagView import *
from FilterView import *
from ViewOne import *

TSIZE = 160 # KBR magic number size of thumbnail

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
appname = 'PyTagger 0.1'


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
        
        #self.grid(row=0,column=0,sticky=tk.NW)
        #vbar.grid(row=0,column=1,sticky=tk.E)
        #hbar.grid(row=1,column=0,sticky=tk.S)

        vbar.config(command=self.yview)                # call on scroll move
        hbar.config(command=self.xview)
        self.config(yscrollcommand=vbar.set)           # call on canvas move
        self.config(xscrollcommand=hbar.set)


canvas = None # TODO HACK
btnSelected = [] # TODO HACK
unSelectedColor = None

def singleClick(btn, imgdir, fileimpacted, tagwin):
    # Single mouse click handling (selection). 
    global canvas # TODO HACK
    global btnSelected # TODO HACK
    global unSelectedColor # TODO HACK
        
    # Revert any previously selected thumbnail.
    if len(btnSelected) != 0:
      for btn2 in btnSelected:
        try:
            btn2.config(bg=unSelectedColor, activebackground=unSelectedColor)  
        except:
            pass # button may be in another window?
      canvas.update()
      
    #print(f"KBR: click {btn} {imgdir} {fileimpacted}")
    btnSelected = []
    btnSelected.append(btn)
    selectBtn(btn)
    
    tagwin.showImage(fileimpacted) # Notify tag window
    
def selectBtn(btn): # TODO canvas class method
    global canvas
    btn.configure(relief='sunken') # TODO needs more obvious indication
    btn.configure(bg='red',activebackground='red')
    canvas.update()

def unSelectBtn(btn): # TODO canvas class method
    global canvas
    global unSelectedColor # TODO HACK
    btn.configure(relief='raised') # TODO needs more obvious indication
    btn.configure(bg=unSelectedColor, activebackground=unSelectedColor)  
    canvas.update()
  
def ctrlClick(btn, imgdir, fileimpacted, tagwin):
    global btnSelected
    
    if btn in btnSelected:
      btnSelected.remove(btn) # remove from existing selection
      unSelectBtn(btn)
      tagwin.removeImage(fileimpacted)
    else:
      btnSelected.append(btn) # add to selected buttons
      selectBtn(btn)
      tagwin.anotherImage(fileimpacted) # Notify tag window

def updateCanvas(canvas, btns, tagwin): # TODO canvas class method
    global unSelectedColor

    canvas.delete('all')
    numthumbs = len(btns)
    if numthumbs == 0:
      return # nothing to do

    linksize = TSIZE + 8

    width = int(canvas.winfo_width())
    height = int(canvas.winfo_height())
    numcols = int(width / linksize)
    numrows = int(math.ceil(numthumbs / numcols))

    fullsize = (0, 0,                                   # upper left  X,Y
        (linksize * numcols), (linksize * numrows) )    # lower right X,Y
    canvas.config(scrollregion=fullsize)                # scrollable area size

    rowpos = 0
    while btns:
        thumbsrow, btns = btns[:numcols], btns[numcols:]
        colpos = 0
        for abtn in thumbsrow:    
            canvas.create_window(colpos, rowpos, anchor=NW,
                    window=abtn, width=linksize, height=linksize)
            colpos += linksize
        rowpos += linksize

      
def buildCanvas(canvas, dirwinsize, numcols, thumbs, tagwin):
    global unSelectedColor

    win = canvas.master
    
    width, height = dirwinsize                      # [SA] new configs model
    numthumbs = len(thumbs)
    
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

    linksize += 8 # KBR add some padding around the image for highlight
    
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
            link.imgfile = imgfile
            allbtns.append(link) # keep reference to avoid gc
            
            def handler1(event, _link=link, _imgfile=imgfile):
                singleClick(_link, win.imgdir, _imgfile, tagwin)
            link.bind('<Button-1>', handler1)
            
            def handler3(event, _link=link, _imgfile=imgfile):
                ctrlClick(_link, win.imgdir, _imgfile, tagwin)
            link.bind('<Control-Button-1>', handler3)

            def handler2(event, _imgfile=imgfile):
                ViewOne(win.imgdir, _imgfile, dirwinsize, viewsize, canvas.master, nothumbchanges, tagwin, appname)
                #ViewOne(imgdir, _imgfile, dirwinsize, viewsize, win, nothumbchanges)
            link.bind('<Double-1>', handler2)
            
        # TODO shift+click to select range of images
            
            #link.pack(side=LEFT, expand=YES, padx=4, pady=4) # appears to be unnecessary?
            canvas.create_window(colpos, rowpos, anchor=NW,
                    window=link, width=linksize, height=linksize)
            colpos += linksize
            savephotos.append(photo)
        rowpos += linksize
        
    if unSelectedColor == None and len(allbtns) > 0:
      unSelectedColor = allbtns[0].cget("background")
      
    return savephotos, allbtns

def complexFilter(tagwin, thumbs, searchlist):
    searchset = set(searchlist)
    subthumbs = []
    for thumbtuple in thumbs:
        ok, imagetags = tagwin.getImgTags(thumbtuple[0])
        if ok and len(imagetags):
            # TODO should be in TagView.py
            taglist = [i.lower() for i in imagetags if i] # remove empty strings; all lowercase
            
            # true: all search tags are in the image tag set (a AND b AND c)
            if searchset <= set(taglist):
                subthumbs.append(thumbtuple)
    return subthumbs

def complexFilter(tagwin, btns, searchlist):
    searchset = set(searchlist)
    subthumbs = []
    for btn in btns:
        ok, imagetags = tagwin.getImgTags(btn.imgfile)
        if ok and len(imagetags):
            # TODO should be in TagView.py
            taglist = [i.lower() for i in imagetags if i] # remove empty strings; all lowercase
            
            # true: all search tags are in the image tag set (a AND b AND c)
            if searchset <= set(taglist):
                subthumbs.append(btn)
    return subthumbs

def simpleFilter(tagwin, btns, taggedonly):
  # identify tagged / untagged
    subthumbs = []
    for btn in btns:
        ok, tags = tagwin.getImgTags(btn.imgfile)
        
        tags = [i.lower() for i in tags if i] # remove empty strings; all lowercase
        
        if taggedonly:
            if ok and len(tags):
                subthumbs.append(btn)
        else:
            if ok and not len(tags):
                subthumbs.append(btn)
    return subthumbs                

def onViewAll(win, canvas):
    updateCanvas(canvas, win.currbtns, win.tagwin)

def onTaggedOnly(win):
    subthumbs = simpleFilter(win.tagwin, win.currbtns, True)
    updateCanvas(canvas, subthumbs, win.tagwin)

def onUnTaggedOnly(win):
    subthumbs = simpleFilter(win.tagwin, win.currbtns, False)
    updateCanvas(canvas, subthumbs, win.tagwin)

def searchExec(win, taglist): # TODO Need 'win' as a callback arg
    if taglist == None:
      # TODO HACK track that the dialog was closed to allow multiple creates
      win.filterview = None
      return
      
    subthumbs = complexFilter(win.tagwin, win.currbtns, taglist)
    updateCanvas(canvas, subthumbs, win.tagwin)

def onFilter(parentwin):
    if parentwin.filterview: # filter is active
        return
    tagw = parentwin.tagwin
    masterlist = tagw.getAllTags()
    fview = FilterView(masterlist, searchExec, parentwin)
    parentwin.filterview = fview

def selectAll(win):
    global btnSelected
    tagw = win.tagwin
    btnSelected = []
    count = len(win.savephotos)
    if count < 1:
      return
      
    tagw.showImage(win.currbtns[0].imgfile) # HACK have to start with an image/tag set
    for btn in win.currbtns:
      btnSelected.append(btn)
      selectBtn(btn)
      tagw.anotherImage(btn.imgfile) # Notify tag window

def resize(win,event):
  global canvas # HACK
  if canvas is not None:
    # TODO this resets to all the buttons, want only the actual current buttons which aren't tracked
    updateCanvas(canvas, win.master.currbtns, win.master.tagwin)
    
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
    
        
    win = kind()
    win.imgdir = imgdir
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
    tagg = Button(tools, text=' Tagged ', command=lambda: onTaggedOnly(win))
    tagg.pack(side=LEFT, expand=YES)
    untag = Button(tools, text=' Untagged ', command=lambda: onUnTaggedOnly(win))
    untag.pack(side=LEFT, expand=YES)
    filt = Button(tools, text=' Filter ', command=lambda: onFilter(win))
    filt.pack(side=LEFT, expand=YES)
    
    # [SA] question=? but portable, help key in all gadgets
    win.bind('<KeyPress-question>', lambda event: onHelp(win))

    tagwin=TagView(imgdir)
    tagwin.initScan()

    # make or load thumbs ==> [(imgfile, imgobj)]
    thumbs = makeThumbs(imgdir,                             # all images in folder
                        size=(TSIZE, TSIZE),                # fixed thumbnails size
                        busywindow=win,                     # announce in GUI
                        nothumbchanges=nothumbchanges,      # don't detect changes? 
                        _tagswin=tagwin)
                        
    tagwin.doneScan()
    
    width, height = dirwinsize                      # [SA] new configs model
    canvas = ScrolledCanvas(win)                    # init viewable window size
    canvas.config(height=height, width=width)       # changes if user resizes

    # NOTE: keeping reference to avoid gc
    win.savephotos, win.currbtns = buildCanvas(canvas, dirwinsize, numcols, thumbs, tagwin)
    win.fullthumbs = thumbs
    
    win.tagwin     = tagwin
    win.imgdir     = imgdir
    win.filterview = None
    
    # bind keys/events for this directory-view window
    win.bind('<KeyPress-d>', 
        lambda event: onDirectoryOpen(win, dirwinsize, viewsize, nothumbchanges))

    win.bind('<KeyPress-t>', lambda event: onTaggedOnly(win)  )
    win.bind('<KeyPress-u>', lambda event: onUnTaggedOnly(win))
    win.bind('<KeyPress-r>', lambda event: onViewAll(win, canvas))
    
    # [SA] bind arrow keys to scroll canvas too (tbd: increment?)
    win.bind('<Up>',    lambda event: canvas.yview_scroll(-1, 'units'))
    win.bind('<Down>',  lambda event: canvas.yview_scroll(+1, 'units'))
    win.bind('<Left>',  lambda event: canvas.xview_scroll(-1, 'units'))
    win.bind('<Right>', lambda event: canvas.xview_scroll(+1, 'units'))
    
    win.bind('<Destroy>', lambda event: cleanup(win))
    
    win.bind('<Control-a>', lambda event: selectAll(win))
    canvas.bind('<Configure>', lambda event: resize(canvas,event))
    
    win.focus()   # [SA] on Windows, make sure new window catches events now
    return win


############################################################################
# Utilities, having multiple class and non-class clients
############################################################################
def cleanup(win):
    if win.tagwin:
        win.tagwin.destroy()
    if win.filterview:
        win.filterview.destroy()

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

def onQuit(parentwin):
    cleanup(parentwin)
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
