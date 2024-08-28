import os
import sys
import pyexiv2
import mimetypes

def isImageFileName(filename):
    """
    ---------------------------------------------------------------------------
    [SA] Detect images by filename's mimetype (not hardcoded set)
    ---------------------------------------------------------------------------
    """
    mimetype = mimetypes.guess_type(filename)[0]                    # (type?, encoding?)
    return mimetype != None and mimetype.split('/')[0] == 'image'   # e.g., 'image/jpeg'

def getTags(imagePath):
    try:
        with pyexiv2.Image(imagePath) as img:
            res = img.read_raw_xmp()
            if len(res) == 0:
                return True, []
            try:
                return True, img.read_xmp()['Xmp.dc.subject']
            except:
                return True, [] # no Xmp.dc.subject
    except:
        return False, [] # couldn't parse xmp

def lookForTag(taglist, findtag):
    for atag in taglist:
        if atag.lower() == findtag:
            return True
    return False

def replaceTag(imagePath, findtag, newtag):
    with pyexiv2.Image(imagePath) as img:
        xmp = img.read_xmp()
        try:
            taglist = xmp['Xmp.dc.subject']
        except:
            taglist = []
#        try:
#            taglist2 = xmp['Xmp.lr.hierarchicalSubject']
#        except:
#            taglist2 = []

        # use a set in case 'newtag' already exists!
        tagset = set([i.lower() for i in taglist])
        tagset.remove(findtag)
        tagset.add(newtag)
        taglist = list(tagset)
        taglist = [i for i in taglist if i] # remove empty strings

        # pyexiv2 magic
        try:
            img.modify_xmp({'Xmp.dc.subject': taglist}) #", ".join(taglist)})      
            #img.modify_xmp({'Xmp.lr.hierarchicalSubject': ", ".join(taglist)})      
        except:
            print(' *error*')

def walkit(rootPath, findtag, newtag):
    unsupported_formats = (".gif",".svg",".avif") # KBR currently un-tag-able image formats
    
    for root, dirs, files in os.walk(rootPath):
        for filename in files:
            
            fullfile = os.path.join(root, filename)
            if not isImageFileName(fullfile):
                continue
            
            if fullfile.lower().endswith(unsupported_formats):
                continue
            
            isok, tags = getTags(fullfile)
            if not isok or len(tags) == 0:
                continue
            
            if lookForTag(tags, findtag):
                print(f"{fullfile}")
                replaceTag(fullfile, findtag, newtag)
            
    
    

def usage():
    print("Usage: python3 renameTag.py <path to root folder> <tag-to-rename> <new-tag-name>")
    exit()

def existErr(trypath):
    print(f"Folder path '{sys.argv[1]}' doesnt exist!")
    usage()
    
if __name__ == '__main__':
    if len(sys.argv) < 4:
        usage()
    if not os.path.exists(sys.argv[1]):
        existErr(sys.argv[1])
        
    pyexiv2.set_log_level(3) # pyexiv2 magic
    walkit(sys.argv[1], sys.argv[2].lower().strip("'\""), sys.argv[3].lower().strip("'\""))
