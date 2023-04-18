import os, io
import re
from enum import Enum, auto

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

PIXELS_PER_MM = 10
AREA_W_MM = 200
AREA_H_MM = 200

DEBUG=False

class PositionsCalculation(Enum):
    ABSOLUTE = auto()
    RELATIVE = auto()

#reads a cmd and option X, Y, S and F
GRBL_REGEX = """\A(?P<cmd>\S+)\s*(X(?P<X>-?\d+[.0-9]*)\s*|Y(?P<Y>-?\d+[.0-9]*)\s*|S(?P<S>\d+[.0-9]*)\s*|F(?P<F>\d+[.0-9]*)\s*)*"""
r = re.compile(GRBL_REGEX)


#laser with its coordinates in REAL world (assume MM unit)
class Laser:
    X = 0.0
    Y = 0.0
    PowerOn = False
    positionsCalculation = PositionsCalculation.ABSOLUTE

    def __init__(self, x=0.0, y=0.0, power=False) -> None:
        self.X = x
        self.Y = y
        self.PowerOn = power
        self.positionsCalculation = PositionsCalculation.ABSOLUTE

    def fromLaser(template:"Laser") -> "Laser":
        newLaser = Laser()
        newLaser.X = template.X
        newLaser.Y = template.Y
        newLaser.PowerOn = template.PowerOn
        newLaser.positionsCalculation = template.positionsCalculation
        return newLaser


    def __str__(self) -> str:
        return f"X={self.X}, Y={self.Y}, Power={self.PowerOn}, Calculations={self.positionsCalculation.name}"
    
    #Get the positions IN THE IMAGE of the laser
    def toImageXY(self, xoffset:int = 0, yoffset:int = 0):
        return (self.X * PIXELS_PER_MM + xoffset, self.Y * PIXELS_PER_MM + yoffset)
    

#Process a line, assuming l is a COPY of the current laser (or current itself)
def __processLine (l:Laser, match):
    if match.group("X") != None:
        #move X to new pos, skip the "X" letter
        x = float(match.group("X"))
        if l.positionsCalculation == PositionsCalculation.ABSOLUTE:
            l.X = x
        else:
            l.X = l.X + x
    if match.group("Y") != None:
        #move Y to new pos, skip the "Y" letter
        y = float(match.group("Y"))
        if l.positionsCalculation == PositionsCalculation.ABSOLUTE:
            l.Y = y
        else:
            l.Y = l.Y + y


def processFile(filepath:str, targetImage:Image = None, xoffset:int = 0, yoffset:int = 0, color="red", lineWidth:float=2) -> Image:        
    """ Based on a GRBL file content, generates an Image.
    Not every GRBL commands are supported so go ahead and test, fix, contribute.

    The image will be UPSIDE DOWN so remember to flip it (img = img.transpose(Image.FLIP_TOP_BOTTOM))

    :param filepath: FULL PATH to the source GRBL file
    :param targetImage: provide an image to write into, or function will make one based on the PIXELS_PER_MM, AREA_W_MM and AREA_H_MM
    :param xoffset: if you need to write in the image shifted by x pixels (default 0)
    :param yoffset: if you need to write in the image shifted by y pixels (default 0)
    :param color: which color you want the line, ie : "red" or (0,0,255,128) for semi-transparent blue (default "red")
    :param lineWidth: which width you want the line (default 2)

    
    """
    laser = Laser()

    contents = None
    with open(filepath, "r") as f:
        contents = f.readlines()

    img = targetImage
    if targetImage == None:
        img = Image.new("RGBA", (AREA_H_MM * PIXELS_PER_MM, AREA_W_MM * PIXELS_PER_MM), (255,255,255))

    draw = ImageDraw.Draw(img, "RGBA")
        
    for l in contents:
        l = l.strip()

        if l.startswith(";"):
            #skip comments
            continue

        m = r.search(l)
        if not m:
            #skip unknown
            continue
        
        if DEBUG: print (f"DBG: {l} => {m.groupdict()}")

        #------------------------ G0 : move (no trace) -------------------------
        if m.group("cmd") == "G0":
            #Don't reset the power, just don't draw
            #laser.PowerOn = False

            __processLine(laser, match=m)

        #------------------------ G1 : move (and trace) -------------------------
        if m.group("cmd") == "G1":
            #newlaser Power is same as previous by default (so continue what you were doing in sort)
            newlaser = Laser.fromLaser(laser)

            #sometimes when filling G1 is used as a G0 depending on the S value
            if m.group("S") != None:                
                newlaser.PowerOn = int(m.group("S")) != 0

            __processLine(newlaser, match=m)


            #Draw a line?
            if newlaser.PowerOn:
                draw.line((laser.toImageXY(xoffset, yoffset), newlaser.toImageXY(xoffset, yoffset)), fill=color, width=lineWidth)

            #update pos
            laser = newlaser


        #------------------------ G90 : Positions are ABSOLUTE from 0,0 -------------------------     
        if m.group("cmd") == "G90":       
            laser.positionsCalculation = PositionsCalculation.ABSOLUTE

        #------------------------ G91 : Positions are RELATIVE from CURRENT position -------------------------     
        if m.group("cmd") == "G91":       
            laser.positionsCalculation = PositionsCalculation.RELATIVE

        #------------------------ Done. Next line. -------------------------
        if DEBUG: print(f"DBG: laser is at { laser }")
    
    #finished
    return img
