import grbl2image

from PIL import Image

img = grbl2image.processFile("sample.gcode/Test gcode 2.nc", color="blue")

img = grbl2image.processFile("sample.gcode/Test gcode 1.nc", targetImage=img, color="red", voffset=300)
img.show()
