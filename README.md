# grbl2image
Generates an **image** (PNG, JPEG, etc.) from a **GRBL** file (.NC, .GC, ...), in Python using PILlow (python3).

![Turns GRBL code into PNG](https://github.com/AlanFromJapan/grbl2image/blob/main/grbl2image.png?raw=true)

The target is to generate a simply a top view of a GRBL job for my Laser (see *limitations* below). As of now only a subset of the GRBL commands are recognized, and more will be added along the way when their need arise. This is not meant to be the complete solution for all GRBL files, but I'll be taking requests on GitHub so don't hesitate. 

## Limitations 
This is made to support my Laser, not CNC, and this is out of scope even of the end scope of library. There are already good solutions that handle the 3D component of your CNC. This is just a top view of a GRBL file, so if it works with yours CNC good for you!

Therefore GRBL codes that don't make sense for a laser will be ignored and not implemented, but if you have time fork this project!

## Assumptions
I took some assumptions with this code, and the more mature it will get the more flexible it will be. For now, here are a few that are enforced implicitly:
- You work in Metric system (like you should)
- Default coords are ABSOLUTE
- Origin is 0,0
- Work area is 200mm x 200mm with a resolution of 10px/mm (but you can change that - see examples)

## Compatibility / Tested software
So far the tested software and empirically perceived support:
- [LightBurn](https://lightburnsoftware.com/) : Very good (all the jobs I made and tried rendered just fine) 

# Technical details 

## Dependencies
- Pillow the replacement of PIL the image library : `python3 -m pip install pillow`

## Supported GRBL codes
I will add them as I need them, but here are the ones that should work as of now:
- G0 move
- G1 burn
- G90 coords are ABSOLUTE
- G91 coords are RELATIVE

## Sample usage
### Generate an image from GRBL file
```python
import grbl2image_AlanFromJapan.grbl2image as G2I
from PIL import Image

#Generate the PIL Image object based on sample code
img = G2I.processFile("sample.gcode/Test gcode 1.nc", color="blue")
#overlay another job in the same image
img = G2I.processFile("sample.gcode/Test gcode 2.nc", targetImage=img, color="red", yoffset=300)

#final flip because the image 0,0 is top left and for us human it's at the bottom left
img = img.transpose(Image.FLIP_TOP_BOTTOM)

#show popup
img.show()
```
### Change the target image size
Default is 200mm x 200mm at 10px/mm resolution, but you can change that according your laser work area. Tip : better have a bigger image and then scaling down than a small image all along.
```python
import grbl2image_AlanFromJapan.grbl2image as G2I
from PIL import Image

#suppose your laser is a 40cm x 30xm for instance you could use these settings **before** calling processFile()
G2I.PIXELS_PER_MM = 5
G2I.AREA_W_MM = 300
G2I.AREA_H_MM = 400

#Generate the PIL Image object based on sample code
img = G2I.processFile("sample.gcode/Test gcode 1.nc", color="blue")

#final flip because the image 0,0 is top left and for us human it's at the bottom left
img = img.transpose(Image.FLIP_TOP_BOTTOM)

#save
img.save("laser_job_001.png")
```
## Source code
Source is MIT licensed on GitHub : https://github.com/AlanFromJapan/grbl2image