"""
===================================================================
Display help text in an info common dialog on Mac and Windows
(using the platform's normal style), but in a custom text-view
popup window on Linux.  This works around the oddly narrow size 
of info dialogs on Linux; they don't handle larger message text.

This is for relatively simple help displays, as in PyGadgets.
Anything larger is better off shipped as an HTML file and opened
via Python's webbrowser module, or similar (e.g., see PyEdit).

TBD: should there be a go-modal option for the Text window? 
TBD: should non-modal display be selectable by user configs?
TBD: support Mac OS slide-down sheet dialog style as an option?
===================================================================
"""

import sys
from tkinter import *
from tkinter.messagebox import showinfo
from tkinter.scrolledtext import ScrolledText   # not Text, just in case


def showhelp(root, appname, helptext, forcetext=False, setwinicon=None):
    """
    Show helptext as appropriate for platform
    """
    title = appname + ' Help'
    helptext = helptext.strip()   # drop any leading/trailing blanks and \n

    if not sys.platform.startswith('linux') and not forcetext:
        #
        # Assume fits on Mac and Windows: use Tk common dialog,
        # with all the usual cosmetics (e.g., Mac app icon)
        #
        showinfo(title, helptext)
        if root: root.focus_force()   # else Mac Tk 8.5 may leave root inactive
    else:
        #
        # Likely too big for Linux info dialog: use a Toplevel/Text
        # new non-model window (a limited but simple solution)
        #
        win = Toplevel()
        win.title(title)
        if setwinicon: setwinicon(win)          # for Windows/Linux only
        text = ScrolledText(win, wrap='word')   # wrap on word boundaries
        text.config(font='system 0 bold')       # std fam/size, darker better?
        text.pack(expand=YES, fill=BOTH)
        text.insert(END, helptext)


if __name__ == '__main__':
    """
    Test me
    """
    helptext = ('See figure 1.'
                '\n\n'
                'Read The Fine Manual.'
                '\n\n') + 'Words go here\n' * 10
    count = 0
    def onHelp():
        global count
        forcetext = count % 2
        count += 1
        showhelp(main, 'Tester', helptext, forcetext, seticon)

    def seticon(win):
        print('seticon:', win)

    main = Tk()
    Button(main, text='testing 1, 2, 3...', command=onHelp).pack()
    main.mainloop()
