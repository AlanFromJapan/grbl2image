#Doesn't feel like the canonical way to import a package in another folder but for now it works.
#  credits to https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
import sys
sys.path.insert(1, 'src/grbl2image')
import grbl2image as G2I

import os

from PIL import Image

#suppose your laser is a 40cm x 30xm for instance you could use these settings **before** calling processFile()
G2I.PIXELS_PER_MM = 5
G2I.AREA_W_MM = 300
G2I.AREA_H_MM = 400

img, _ = G2I.processFile(os.path.join("tests", "sample.gcode", "Test gcode 1.nc"), color="blue", lineWidth=1)

#final flip
img = img.transpose(Image.FLIP_TOP_BOTTOM)

img.show()
#img.save ("output.png")
