"""
View and edit tags for selected image(s).

A) When one image is selected, the current tags are the image's tags. When
   the tags are written, the image tags are set to the current tags.
B) When multiple images are selected, the current tags are the *intersection*
   of all image tags. I.e. each image may have tags which are not shown in the
   "current" tag list. When the tags are written, each image has the *changes*
   to the common tags applied.

NOTE: any modifications to the "current tags" are lost if an image is added or
removed!
"""
import pyexiv2
import os
from tkinter import *
from tkinter.scrolledtext import *
from CreateToolTip import *

class TagView(Toplevel):

    masterTagList = set()
    origCurrTagList = set()
    currTagList = set()
    image_names = []
    whoisit = None    # any active ViewOne window

    """
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    """
    def __init__(self, imgdir):
        Toplevel.__init__(self)
        self.title(f"Tags:{imgdir}")
        self.folder = imgdir
        self.geometry("550x500")
                
        # header row showing the filename
        self.imgName = Label(self, text="filename here")
        self.imgName.grid(row=0,column=0)

        # 'Active' tags row
        self.currTags = ScrolledText(self, height=7, wrap="word")
        self.currTags.grid(row=1,column=0,pady=3,sticky='nsew')

        # Add-tag row
        addFrame = Frame(self, bg='blue')
        addBtn = Button(addFrame, text = " Add ", command=self.addClick)
        self.addEdit = Entry(addFrame)
        addBtn.grid      (row=0,column=0,padx=3, pady=1)
        self.addEdit.grid(row=0,column=1,padx=3)
        addFrame.grid(row=2,column=0,sticky=W, pady=2, ipady=2)
        CreateToolTip(addBtn,"Create and add a new tag to the image")

        # Buttons row
        blah = Frame(self, bg='green')
        
        self.btnPrev = Button(blah, text=" Prev Image ", command=self.clickPrev)
        self.btnPrev["state"] = DISABLED # TODO pending a file list mediator for thumbs/tag views
        btnReset = Button(blah, text=" Reset ", command=self.clickReset)
        btnWrite = Button(blah, text= " Write ", command=self.clickWrite)
        self.btnNext = Button(blah, text= " Next Image ", command=self.clickNext)
        self.btnNext["state"] = DISABLED # TODO pending a file list mediator for thumbs/tag views
        
        self.btnPrev.grid (row=0,column=0, padx=5, pady=1)
        btnReset.grid(row=0,column=1, padx=5)
        btnWrite.grid(row=0,column=2, padx=5)
        self.btnNext.grid (row=0,column=3, padx=5)
        blah.grid(row=3, column=0, pady=2, ipady=2)

        # Folder-wide tags row
        self.btnFrame = ScrolledText(self, height=12, wrap="word")
        self.btnFrame.grid(row=4,column=0,sticky='nsew',pady=3)

        # Resizing rules
        self.rowconfigure(1, weight=2)
        self.rowconfigure(4, weight=4)
        self.columnconfigure(0, weight=1)
        
        self.update()


        self.allbtns = []
        self.currbtns = []
        pyexiv2.set_log_level(3) # pyexiv2 magic


    def getImgTags(self, imgfile):
        imagePath = os.path.join(self.folder, imgfile)
        try:
            with pyexiv2.Image(imagePath) as img:
                res = img.read_raw_xmp()
                if len(res) == 0:
                    return True, [] # read fail
        #      print(f"|{res[0]}|")
        #      if res[0] != "<":
        #        print(res)
        #        return []
                # TODO problem files so far are missing a leading '<' in the raw xmp
                #print(res)
                try:
                    return True, img.read_xmp()['Xmp.dc.subject']
                except:
                    return True, [] # no Xmp.dc.subject
        except:
            return False, [] # couldn't parse xmp

    # 0
    # 1 has tags
    # 2 error
    def getTags(self, imgfile):
        # For an image in the folder, adds its tags to the folder list

        # read all tags from provided imgfile
        ok, taglist = self.getImgTags(imgfile)
        if not ok:
            return 2

        taglist = [i.lower() for i in taglist if i] # remove empty strings; all lowercase

        # add each to the master tag set 
        self.masterTagList.update(taglist)

        return 0 if len(taglist) == 0 else 1

    def clickReset(self):
        # Reset button clicked: return current taglist to "original"
        self.currTagList.clear()
        self.currTagList.update(self.origCurrTagList)
        self.updateCurrentTags()

    def writeTags(self, imgname, taglist):
      # write tags to an image
        imagePath = os.path.join(self.folder, imgname)
        with pyexiv2.Image(imagePath) as img:
            # pyexiv2 magic
            try:
                img.modify_xmp({'Xmp.dc.subject': taglist})
            except Exception as e:
                print(e) # TODO
                return False
        return True

    def clickNext(self):
      if self.whoisit is not None:
        self.whoisit.onNextImage(None)
        
    def clickPrev(self):
      if self.whoisit is not None:
        self.whoisit.onPrevImage(None)
      
    def clickWrite(self):
      if len(self.image_names) == 0: # TODO disable write btn if no images
        return
        
      if len(self.image_names) == 1:
        # Write button clicked: write current taglist to the file.
        self.writeTags(self.image_names[0], list(self.currTagList)) # TODO failure
        
      else:
        # Update all images with *changes* to taglist
        #print("Write for multiple images")
        #print(f"Curr: {self.currTagList} Orig: {self.origCurrTagList}")
        adds = self.currTagList.difference(self.origCurrTagList) # tags to add
        rems = self.origCurrTagList.difference(self.currTagList) # tags to remove
        #print(f"Adds: {adds} Removes: {rems}")
        for imgname in self.image_names:
            ok, currtags = self.getImgTags(imgname)
            currtags2 = {i.lower() for i in currtags if i} # TODO merge into getImgTags?
            currtags2.difference_update(rems)
            currtags2.update(adds)
            #print(f"{imgname}: before:{currtags} after:{currtags2}")
            self.writeTags(imgname, list(currtags2)) # TODO failure
      self.origCurrTagList = self.currTagList.copy() # new 'original'

    def initScan(self):
        self.masterTagList.clear()

    def getAllTags(self):
        return self.masterTagList
    
    def setTags(self, taglist):
        # incremental testing: initialize to a specific set of tags
        self.masterTagList.update(taglist)

    def addToCurrentTag(self, atag):
        # Add the clicked tag to the current tag list
        self.currTagList.update([atag])
        self.updateCurrentTags()

    def removeCurrentTag(self, atag):
        # remove the clicked tag from the current tag list
        self.currTagList.remove(atag)
        self.updateCurrentTags()

    def favoriteCurrentTag(self, atag):
        # add the clicked tag to the favorites
        print(f"Favoriting: {atag}")

    def updateCurrentTags(self):
        # print(f"current tags:{self.currTagList}")
        # delete all existing widgets
        self.currTags.configure(state="normal") # magic
        self.currTags.delete('1.0', END) 

        # add each tag as a widget      
        if len(self.currTagList) > 0:
            for atag in sorted(list(self.currTagList)):

                handler1 = lambda whichtag=atag: self.removeCurrentTag(whichtag)
                abtn = Button(self.currTags, text=f" {atag} ", padx=2, pady=2, command=handler1)
                # Right-click favorites the tag : binding magic
                abtn.bind("<Button-3>", lambda e,c=atag: self.favoriteCurrentTag(c))
                # TODO tooltip

                self.currTags.window_create("insert", window=abtn, padx=2, pady=2)
                self.currbtns.append(abtn)
        self.currTags.configure(state="disabled") # magic

    def showImage(self, imgname):
        #print(f"User clicked: {imgname}")
        self.imgName.config(text=f" {imgname} ")
        self.image_names = []
        self.image_names.append(imgname)

        # New image: initialize the "current" and "original" taglists      
        self.currTagList.clear()
        self.origCurrTagList.clear()

        ok, taglist = self.getImgTags(imgname)
#        if not ok:
#            return # TODO cannot work with image. Need to reset things.

        #print(f"found tags:{taglist}")
        if ok:
            temp = [i.lower() for i in taglist if i] # remove empty strings; all lowercase
            self.currTagList.update(sorted(temp)) 
            self.origCurrTagList.update(self.currTagList)

        self.updateCurrentTags()

    def anotherImage(self, imgname):
      # User has added another image to the selection set.
      if imgname in self.image_names: # no double-add
        return
        
      self.image_names.append(imgname)
      self.imgName.config(text=f"*Multiple images*")
      
      # determine the new "common tags" list
      ok, taglist = self.getImgTags(imgname) # tags for new image
#        if not ok:
#            return # TODO cannot work with image. Need to reset things.
      
      if ok:
        temp = set(i.lower() for i in taglist if i) # remove empty strings; all lowercase
        inter = temp.intersection(self.origCurrTagList)
        self.currTagList.clear()
        self.currTagList.update(sorted(inter))
        self.origCurrTagList = self.currTagList.copy()
        
      self.updateCurrentTags()

    def removeImage(self, imgname):
      # User has removed an image from the selection set
      if imgname not in self.image_names:
        return
        
      self.image_names.remove(imgname)
      # TODO the list of common tags may have changed - need to rebuild the set from scratch   

    def addToFullTag(self, newtag):
        self.masterTagList.append(newtag)
        self.doneScan()

    def doneScan(self):
        self.masterTagList = sorted(self.masterTagList)
        #print(f"Final tags: {self.masterTagList}" )
        # for each tag in masterTagList
        #   create a button
        self.btnFrame.configure(state="normal")
        self.btnFrame.delete('1.0', END) 
        for atag in self.masterTagList:

#    widget = tk.Label(root, width=12, text=f"Widget #{COUNT}", bd=1, relief="raised",
#                      bg="#5C9BD5", foreground="white", padx=4, pady=4)
#    text.configure(state="normal")
#    text.window_create("insert", window=widget, padx=10, pady=10)
#    text.configure(state="disabled")

            handler = lambda whichtag=atag: self.addToCurrentTag(whichtag)
            abtn = Button(self.btnFrame, text=f" {atag} ", padx=2, pady=2, command=handler)
            self.btnFrame.window_create("insert", window=abtn, padx=2, pady=2)
            # Right-click favorites the tag : binding magic
            abtn.bind("<Button-3>", lambda e,c=atag: self.favoriteCurrentTag(c))

            self.allbtns.append(abtn) # TODO for gc: is this necessary?
        self.btnFrame.configure(state="disabled")

    def addClick(self):
        newtag = self.addEdit.get()
        newtag = newtag.strip().lower()
        if len(newtag) > 0:
            #print(f"will add: >{newtag}<")
            self.addToCurrentTag(newtag)
            self.addToFullTag(newtag)
            self.addEdit.delete(0, END) # clear the edit field

    def ActiveViewOne(self, whichview):
      self.whoisit = whichview
      self.btnPrev["state"] = NORMAL
      self.btnNext["state"] = NORMAL
      
      
if __name__ == '__main__': 

    root = Tk()
    img="tumblr_m7j0nslfOM1qcr6iqo1_1280.jpg"
    folder="/home/kevin/proj/pyTagger/star_wars"
    tagwin = TagView(folder)


    tags = ['art', 'artoo detoo', 'at-st', 'captain ribman', 'cat staggs', 'celebration v', 'design', 'enlist today', 'film', 'football', 'graphic design', 'hoth', 'illustration', 'japan', 'lego', 'logo', 'mondotees', 'pin-up', 'princess leia', 'propaganda', 'r2-d2', 'raiders', 'rebellion', 'recruitment', 'samurai wars', 'sandpeople', 'sci fi', 'science fiction', 'shan jiang', 'snowtrooper', 'space', 'star wars galaxies', 'stormtrooper', 'tatooine', 'the empire strikes back', 'to hoth and back', 'tusken raiders', 'walker']
#    tagwin=TagView("")
    tagwin.initScan()
    tagwin.setTags(tags)
    tagwin.doneScan()

    tagwin.showImage(img)

    tagwin.mainloop()
