import pyexiv2
import os
from tkinter import *

class TagView(Toplevel):
  
    masterTagList = set()
    origCurrTagList = set()
    currTagList = set()

    """
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    """
    def __init__(self, imgdir):
        Toplevel.__init__(self)
        self.title(f"Tags:{imgdir}")
        self.folder = imgdir
        self.geometry("450x500")
        self.update()
        
        self.imgName = Label(self, text="filename here")
        self.imgName.pack(side=TOP, fill=X)
        
        
        aFrame = Frame(self)
        
        self.currTags = Text(aFrame, height=10, wrap="word", yscrollcommand=lambda *args: vsbCT.set(*args))
        vsbCT = Scrollbar(aFrame, command=self.currTags.yview)
        vsbCT.pack(side="right", fill="y")
        self.currTags.pack(side="left",fill="both", expand=NO)
        
        aFrame.pack()
        #aFrame.config(width=400,height=200)
        #aFrame.update()

        addFrame = Frame(self, bg='blue')
        addFrame.pack(fill=X)
        
        addBtn = Button(addFrame, text = " Add ", command=self.addClick)
        addBtn.pack(side=LEFT, expand=NO, padx=5)
        self.addEdit = Entry(addFrame)
        self.addEdit.pack(side=LEFT,expand=NO)
                
        blah = Frame(self, bg='green')
        #blah.pack(side=BOTTOM, fill=X)
        blah.pack(fill=X)
        
#        test = Button(blah, text=' Test ')   # [SA] no bg= on Mac
#        test.pack(side=RIGHT, expand=YES)
        btnReset = Button(blah, text=" Reset ", command=self.clickReset, padx=3)
        btnReset.pack(side=LEFT, expand=YES)
        btnWrite = Button(blah, text= " Write ", command=self.clickWrite)
        btnWrite.pack(side=LEFT, expand=YES)

        bFrame = Frame(self)
        self.btnFrame = Text(bFrame, wrap="word", yscrollcommand=lambda *args: vsb.set(*args))
        vsb = Scrollbar(bFrame, command=self.btnFrame.yview)
        vsb.pack(side="right", fill="y")
        self.btnFrame.pack(side="left",fill="both", expand=False)
        #self.btnFrame.config(width=400,height=200)

        bFrame.pack()

#        self.btnFrame = Frame(self, bg='blue')
#        self.btnFrame.pack(side=TOP)
#        self.btnFrame.config(width=500,height=500)
        
        self.allbtns = []
        self.currbtns = []
        
        #self.masterTagList = {}
        
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
        
    def getTags(self, imgfile):
      # For an image in the folder, adds its tags to the folder list
      
      # read all tags from provided imgfile
      ok, taglist = self.getImgTags(imgfile)
      if not ok:
        return

      taglist = [i.lower() for i in taglist if i] # remove empty strings; all lowercase
      
      # add each to the master tag set 
      self.masterTagList.update(taglist)
      
    def clickReset(self):
      # Reset button clicked: return current taglist to "original"
      self.currTagList.clear()
      self.currTagList.update(self.origCurrTagList)
      self.updateCurrentTags()
      
    def clickWrite(self):
      # Write button clicked: write current taglist to the file.
      
      imgfile = self.imgName.cget("text").strip()
      imagePath = os.path.join(self.folder, imgfile)
      # TODO exceptions?
      with pyexiv2.Image(imagePath) as img:
        # pyexiv2 magic
        img.modify_xmp({'Xmp.dc.subject': ", ".join(self.currTagList)})      
        img.modify_xmp({'Xmp.lr.hierarchicalSubject': ", ".join(self.currTagList)}) 

      self.origCurrTagList.clear()        
      self.origCurrTagList.update(self.currTagList) # new 'original'
      
    def initScan(self):
      self.masterTagList.clear()
      
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

    def updateCurrentTags(self):
      #print(f"current tags:{self.currTagList}")
      # delete all existing widgets
      self.currTags.configure(state="normal") # magic
      self.currTags.delete('1.0', END) 

      # add each tag as a widget      
      if len(self.currTagList) > 0:
        for atag in sorted(list(self.currTagList)):
          
          handler = lambda whichtag=atag: self.removeCurrentTag(whichtag)
          abtn = Button(self.currTags, text=f" {atag} ", padx=2, pady=2, command=handler)
          # TODO tooltip
          
          self.currTags.window_create("insert", window=abtn, padx=2, pady=2)
          self.currbtns.append(abtn)
      self.currTags.configure(state="disabled") # magic
            
    def showImage(self, imgname):
      #print(f"User clicked: {imgname}")
      self.imgName.config(text=f" {imgname} ")
                    
      ok, taglist = self.getImgTags(imgname)
      if not ok:
        return # TODO cannot work with image. Need to reset things.

      #print(f"found tags:{taglist}")

      # New image: initialize the "current" and "original" taglists      
      self.currTagList.clear()
      self.origCurrTagList.clear()
      temp = [i.lower() for i in taglist if i] # remove empty strings; all lowercase
      self.currTagList.update(sorted(temp)) 
      self.origCurrTagList.update(self.currTagList)

      self.updateCurrentTags()
      
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
