# grbl2image
Generates an **image** (PNG, JPEG, etc.) from a **GRBL** file (.NC, .GC, ...), in Python using PILlow (python3).

![Turns GRBL code into PNG](https://github.com/AlanFromJapan/grbl2image/blob/main/grbl2image.png?raw=true)

The target is to generate a simply a top view of a GRBL job for my Laser (see *limitations* below). As of now only a subset of the GRBL commands are recognized, and more will be added along the way when their need arise.

## Limitations 
This is made to support my Laser, not CNC, and this is out of scope even of the end scope of this. There are already good solutions that handle the 3D component of your CNC. This is just a top view of a GRBL file, so if it works with yours CNC good for you!

Therefore GRBL codes that don't make sense for a laser will be ignored and not implemented, but if you have time fork this project!

## Assumptions
I took some assumptions with this code, and the more mature it will get the more flexible it will be. For now, here are a few that are enforced implicitly:
- You work in Metric system (like you should)
- Default coords are ABSOLUTE
- Origin is 0,0

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

```python
import grbl2image_AlanFromJapan.grbl2image as G2I
from PIL import Image

#Generate the PIL Image object based on sample code
img1 = G2I.processFile("sample.gcode/Test gcode 1.nc", color="blue")
img2 = G2I.processFile("sample.gcode/Test gcode 2.nc", color="red", yoffset=300)

#final flip because the image 0,0 is top left and for us human it's at the bottom left
img2 = img2.transpose(Image.FLIP_TOP_BOTTOM)

#show popup
img2.show()
```

## Source code
(Source is MIT licensed on GitHub)[https://github.com/AlanFromJapan/grbl2image]