import grbl2image
import os

from PIL import Image

img = grbl2image.processFile(os.path.join("sample.gcode", "Test gcode 2.nc"), color="blue")

img = grbl2image.processFile(os.path.join("sample.gcode", "Test gcode 1.nc"), targetImage=img, color="red", yoffset=300)

#img = grbl2image.processFile("sample.gcode/Tokens 6 - Parnast final.nc", targetImage=img, color="black", yoffset=600)

#final flip
img = img.transpose(Image.FLIP_TOP_BOTTOM)

img.show()
#img.save ("output.png")
