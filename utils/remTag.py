import asyncio
import os
import pyexiv2
import sys

def getTags(imagePath):
  try:
    with pyexiv2.Image(imagePath) as img:
      res = img.read_raw_xmp()
      if len(res) == 0:
#        print("***Read fail")
        return True, []
#      print(f"|{res[0]}|")
#      if res[0] != "<":
#        print(res)
#        return []
      # TODO problem files so far are missing a leading '<' in the raw xmp
      #print(res)
      try:
        return True, img.read_xmp()['Xmp.dc.subject']
      except:
        #print("Except2")
        return True, [] # no Xmp.dc.subject
  except:
#      print("***Error parsing xmp")
      return False, [] # couldn't parse xmp

def remTag(imagePath, tag):
    with pyexiv2.Image(imagePath) as img:
      xmp = img.read_xmp()
      
      taglist = xmp['Xmp.dc.subject']
      try:
        taglist2 = xmp['Xmp.lr.hierarchicalSubject']
      except:
        taglist2 = []
      taglist.remove(tag)
      print(imagePath)
      
      if len(taglist) == 0:
        # TODO need to figure out how to remove the key altogether
        img.modify_xmp({'Xmp.dc.subject': ""})      
        img.modify_xmp({'Xmp.lr.hierarchicalSubject': ""})      
      else:  
#      xmp['Xmp.dc.subject'] = taglist
        # pyexiv2 magic
        img.modify_xmp({'Xmp.dc.subject': ", ".join(taglist)})      
        img.modify_xmp({'Xmp.lr.hierarchicalSubject': ", ".join(taglist)})      
#      print(xmp)
#      img.modify_xmp(xmp)
      
####################################################
# Main

#image_exts = ['.jpg','.jpeg','.gif','.png','.webp'] # .gif exception
image_exts = ['.jpg','.jpeg','.png','.webp']  

if len(sys.argv) < 3:
  print("Usage: addtag <path> <tag>")
  exit()

path = sys.argv[1]  
if not os.path.exists(path):
  print(f"not exist")
  exit()

tag = sys.argv[2]
print(f"Adding: '{tag}'")

pyexiv2.set_log_level(3)
  
for f in os.listdir(path):
  
  # image files only
  ext = os.path.splitext(f)[1]
  if ext not in image_exts:
    continue
  
  #print(f'{f}--------------------------')
  file_path = os.path.join(path, f)
  ok, taglist = getTags(file_path)

  if not ok:
    print(f'{f} : error')

  if tag not in taglist:
    print(f"{f} doesn't have tag")
  else:
    remTag(file_path,tag)
        
#  if len(taglist) != 0:
#    print(f'{f} : {taglist}')
