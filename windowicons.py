"""
[SA] shamelessly adapted (mostly stolen) from frigcal's code
"""

import os, sys
from tkinter import Tk, Toplevel, PhotoImage

RunningOnMac     = sys.platform.startswith('darwin')    # all Mac OS (X)
RunningOnWindows = sys.platform.startswith('win')       # all Windows
RunningOnLinux   = sys.platform.startswith('linux')     # all Linux


def trySetWindowIcon(window, icondir='icons', iconname='pygadgets', altprefix='../../'):
    """
    ----------------------------------------------------------------------
    Replace a Tk() or Toplevel() window's generic Tk icon with a custom
    icon for the client program.  This is inherently platform-specific: 

      Windows:
        uses '.ico' files and iconbitmap() in all Tks to set the 
        icon used for window borders and taskbar entries

      Linux: 
        uses '.gif' files and Tk 8.5+'s iconphoto() to set app-bar 
        icon; there may be additional options, not used here

      Mac:
        is not supported (icons on Mac require an app bundle), but 
        is ruled out explicitly to avoid a generic border icon

    Where applicable, the icon is applied to main window and all popup 
    windows, including dialogs (they are inherited in window trees).

    Note that the use of GIF files on Linux stems from limitations
    of Tk's PhotoImage(): PNGs work in Tk 8.6+ and most types work 
    with a third-party Pillow install, but Tk 8.5- is largely GIFs. 

    The altprefix is for bundling and structure differences.  PyGadgets
    spawns gadgets in its own folder for apps and source, and frozen 
    exes and executables run in a common install folder (all '.'), but 
    standalone source-code gadgets may run in their own folders (../..).

    Caveat: under Tk 8.6, the app-bar icon isn't currently set on Linux 
    for PyClock only (despite mutiple recoding attempts).  All other 
    gadgets do set their icon on Linux using the same image file and 
    identical code; this happens whether Pillow is used or not; the icon 
    file's pathname is valid; and the Tk call that sets icons for Linux 
    runs without exceptions.  TBD, but this seems a bug in Linux Tk 8.6.
    ----------------------------------------------------------------------
    """
    if not isinstance(window, (Tk, Toplevel)):
        print('Cannot set icon on non-toplevel widget')
        return 

    if not os.path.exists(icondir):
        icondir = altprefix + icondir   # e.g., not in '.': try other

    iconname += '.ico' if RunningOnWindows else '.gif'
    iconpath = os.path.join(icondir, iconname)
    iconpath = os.path.normpath(iconpath)

    try:
        if RunningOnWindows:
            # Windows (only?), all contexts
            window.iconbitmap(default=iconpath)     # this and all its children
            
        elif RunningOnLinux:
            # Linux (only?), Tk 8.5+, app bar
            imgobj = PhotoImage(file=iconpath)
            window.iconphoto(True, imgobj)          # arg1 is default= setting
            window._pygadgets_icon_image = imgobj   # save reference (required?)
            
        elif RunningOnMac or True:
            # Mac OS X: neither of the above work, use app bundles instead
            raise NotImplementedError

    except Exception as why:
        pass   # bad file or platform

