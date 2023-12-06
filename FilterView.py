# TODO first clause could be NOT!

from tkinter import *
from tkinter.scrolledtext import *
from CreateToolTip import *

class FilterView(Toplevel):
    
    masterTagList = set()
    
    def __init__(self, alltags, callbackfunction):
        Toplevel.__init__(self)
        self.masterTagList = alltags
        self.geometry("500x500")
        
        # text entry row
        self.tag1 = Text(self, height=1.5, width=30, name="entry1")
        self.tag1.grid( row=0, column=1)
        
        # text entry row
        self.chk2 = Checkbutton(self, text="And Not")
        self.chk2.grid( row=1, column=0, sticky=E, padx=3)
        self.tag2 = Text(self, height=1.5, width=30, name="entry2")
        self.tag2.grid( row=1, column=1, sticky=W)

        # text entry row
        self.chk3 = Checkbutton(self, text="And Not")
        self.chk3.grid( row=2, column=0)
        self.tag3 = Text(self, height=1.5, width=30, name="entry3")
        self.tag3.grid( row=2, column=1)

        # text entry row
        self.chk4 = Checkbutton(self, text="And Not")
        self.chk4.grid( row=3, column=0)
        self.tag4 = Text(self, height=1.5, width=30, name="entry4")
        self.tag4.grid( row=3, column=1)
        
        # buttons row
        blah = Frame(self, bg='green')
        btnFav   = Button(blah, text=" Fav ")
        btnReset = Button(blah, text=" Reset ", command=self.clickReset)
        btnDoit  = Button(blah, text= " Do It ", command=self.clickWrite)
        btnFav.grid  (row=0,column=0,padx=5,pady=1)
        btnReset.grid(row=0,column=1,padx=5)
        btnDoit.grid (row=0,column=2,padx=5)
        blah.grid(row=4, column=1, columnspan=1, pady=2, ipady=2)
        
        # Folder-wide tags row
        self.btnFrame = ScrolledText(self, height=12, wrap="word")
        self.btnFrame.grid(row=5,column=0,columnspan=2,sticky='nsew',pady=3)
        
        self.updateCurrentTags()
        
        #self.rowconfigure(1, weight=2)
        self.rowconfigure(5, weight=4)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.update()
        self.tag1.focus() # start focus at first entry

        self.clauses = ['','','','']
        self.widgets = [self.tag1, self.tag2, self.tag3, self.tag4]
        self.callback = callbackfunction
        
    def clearItem(self, index):
        target = self.widgets[index]
        target.configure(state="normal")
        target.delete('1.0', END)
        target.configure(state="disabled")
        self.clauses[index] = ''
        
    def clickReset(self):
        self.clearItem(0)
        self.clearItem(1)
        self.clearItem(2)
        self.clearItem(3)
#        self.clearItem(self.tag1)
#        self.clearItem(self.tag2)
#        self.clearItem(self.tag3)
#        self.clearItem(self.tag4)
        self.tag1.focus() # start focus at first entry
        # TODO reset boolean widgets
    
    def clickWrite(self):
        clauses = [i.lower() for i in self.clauses if i] # remove empty strings; all lowercase
        if self.callback is not None:
            self.callback(self.clauses)
#        for i in range(4):
#            val = self.clauses[i]
#            if val != '':
#                print(f"{self.clauses[i]}")
        pass
    
    def addToCurrentTag(self, atag):
        # put the selected tag in the current Entry
        who = self.focus_get()
        who2 = str(who).split(".")[-1]
        print(f"{who2}")
        match who2:
            case 'entry1':
                target = self.tag1
                index = 0
                focustarget = self.tag2
            case 'entry2':
                target = self.tag2
                index = 1
                focustarget = self.tag3
            case 'entry3':
                target = self.tag3
                index = 2
                focustarget = self.tag4
            case 'entry4':
                target = self.tag4
                index = 3
                focustarget = self.tag1
            case _:
                return

        # Add the tag to the CURRENT entry
        target.configure(state="normal")
        target.delete('1.0', END)
        # click the button to remove it
        abtn = Button(target, text=f" {atag} ", command=lambda: self.clearItem(index))
        target.window_create("insert", window=abtn, padx=2, pady=2)
        target.configure(state="disabled")
        focustarget.focus() # set focus to the NEXT entry
        self.clauses[index] = atag
    
    def updateCurrentTags(self):
        self.masterTagList = sorted(self.masterTagList)
        
        # for each tag in masterTagList
        #   create a button
        
        self.btnFrame.configure(state="normal")
        self.btnFrame.delete('1.0', END) 
        for atag in self.masterTagList:

            handler = lambda whichtag=atag: self.addToCurrentTag(whichtag)
            abtn = Button(self.btnFrame, text=f" {atag} ", padx=2, pady=2, command=handler)
            self.btnFrame.window_create("insert", window=abtn, padx=2, pady=2)

        self.btnFrame.configure(state="disabled")

def testcall(taglist):
    for i in range(4):
        val = taglist[i]
        if val != '':
            print(f"{taglist[i]}")
    
if __name__ == '__main__': 

    root = Tk()
    tags = ['art', 'artoo detoo', 'at-st', 'captain ribman', 'cat staggs', 'celebration v', 'design', 'enlist today', 'film', 'football', 'graphic design', 'hoth', 'illustration', 'japan', 'lego', 'logo', 'mondotees', 'pin-up', 'princess leia', 'propaganda', 'r2-d2', 'raiders', 'rebellion', 'recruitment', 'samurai wars', 'sandpeople', 'sci fi', 'science fiction', 'shan jiang', 'snowtrooper', 'space', 'star wars galaxies', 'stormtrooper', 'tatooine', 'the empire strikes back', 'to hoth and back', 'tusken raiders', 'walker']
    fwin = FilterView(tags, testcall)
    fwin.mainloop()

                 
