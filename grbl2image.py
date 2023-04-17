import os, io
import re
from enum import Enum, auto

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

PIXELS_PER_MM = 10
AREA_W_MM = 200
AREA_H_MM = 200

class PositionsCalculation(Enum):
    ABSOLUTE = auto()
    RELATIVE = auto()

#reads a cmd and option X, Y, S and F
GRBL_REGEX = """\A(?P<cmd>\S+)\s+((?P<X>X\d+[.0-9]*)\s*|(?P<Y>Y\d+[.0-9]*)\s*|(?P<S>S\d+)\s*|(?P<F>F\d+)\s*)*"""
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

    def __str__(self) -> str:
        return f"X={self.X}, Y={self.Y}, Power={self.PowerOn}"
    
    #Get the positions IN THE IMAGE of the laser
    def tupleXY(self, voffset:int = 0,):
        return (self.X * PIXELS_PER_MM, self.Y * PIXELS_PER_MM + voffset)
    

    


def processFile(filepath:str, targetImage:Image = None, voffset:int = 0, color=None) -> Image:        
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
        
        print (f"DBG: {l} => {m.groupdict()}")

        #------------------------ G0 : move (no trace) -------------------------
        if m.group("cmd") == "G0":
            #Don't reset the power, jsut don't draw
            #laser.PowerOn = False

            if m.group("X") != None:
                #move X to new pos, skip the "X" letter
                x = float(m.group("X")[1:])
                laser.X = x
            if m.group("Y") != None:
                #move Y to new pos, skip the "Y" letter
                y = float(m.group("Y")[1:])
                laser.Y = y

        #------------------------ G1 : move (and trace) -------------------------
        if m.group("cmd") == "G1":
            #newlaser Power is same as previous by default (so continue what you were doing in sort)
            newlaser = Laser(x=laser.X, y=laser.Y, power=laser.PowerOn)

            #sometimes when filling G1 is used as a G0 depending on the S value
            if m.group("S") != None:                
                newlaser.PowerOn = int(m.group("S")[1:]) != 0

            if m.group("X") != None:
                #move X to new pos, skip the "X" letter
                x = float(m.group("X")[1:])
                newlaser.X = x
            if m.group("Y") != None:
                #move Y to new pos, skip the "Y" letter
                y = float(m.group("Y")[1:])
                newlaser.Y = y


            #Draw a line?
            if newlaser.PowerOn:
                draw.line((laser.tupleXY(voffset), newlaser.tupleXY(voffset)), fill=color, width=2)

            #update pos
            laser = newlaser


        #------------------------ G90 : Positions are ABSOLUTE from 0,0 -------------------------     
        if m.group("cmd") == "G90":       
            laser.positionsCalculation = PositionsCalculation.ABSOLUTE

        #------------------------ G91 : Positions are RELATIVE from CURRENT position -------------------------     
        if m.group("cmd") == "G91":       
            laser.positionsCalculation = PositionsCalculation.RELATIVE

        #------------------------ Done. Next line. -------------------------
        print(f"DBG: laser is at { laser }")
    
    #finished
    return img
