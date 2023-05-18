#Doesn't feel like the canonical way to import a package in another folder but for now it works.
#  credits to https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
import sys
sys.path.insert(1, 'src/grbl2image')
import grbl2image as G2I

import os

from PIL import Image

samplesPath = os.path.join("tests", "sample.gcode")
#list of files
l = [l for l in os.listdir(samplesPath) if os.path.isfile(os.path.join(samplesPath, l)) and l.lower()[-3:] in ['.nc', '.gc']]

for f in l:
    print (f)
    img, stats = G2I.processFile(os.path.join(samplesPath, f), color="blue")
    print(stats)
    
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    
    img.save(os.path.join(samplesPath, f[:-3] + ".png"))

#img.show()
#img.save ("output.png")
