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

tags_dict = {}
def accumulateTags(taglist):
    for atag in taglist:
        lc = atag.lower()
        x = tags_dict.get(lc)
        if x is None:
            tags_dict[lc] = 1
        else:
            tags_dict[lc] += 1

def lookForTag(taglist, findtag):
    for atag in taglist:
        if atag.lower() == findtag:
            return True
    return False

def walkit(rootPath, findtag):
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
            
    
    

def usage():
    print("Usage: python3 findbytag.py <path to root folder> <tag>")
    exit()

def existErr(trypath):
    print(f"Folder path '{sys.argv[1]}' doesnt exist!")
    usage()
    
if __name__ == '__main__':
    if len(sys.argv) < 3:
        usage()
    if not os.path.exists(sys.argv[1]):
        existErr(sys.argv[1])
        
    pyexiv2.set_log_level(3) # pyexiv2 magic
    walkit(sys.argv[1], sys.argv[2].lower().strip("'\""))