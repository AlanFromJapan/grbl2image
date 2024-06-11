import os
import math
import re
from enum import Enum, auto

from PIL import Image
from PIL import ImageDraw
from PIL import ImageColor

PIXELS_PER_MM = 10
AREA_W_MM = 200
AREA_H_MM = 200
BG_COLOR = (255,255,255,255)
NO_BLENDING = False #if True, the laser power will be ignored and the line will be drawn without alpha blending (ON/OFF mode)

DEBUG=False

class PositionsCalculation(Enum):
    ABSOLUTE = auto()
    RELATIVE = auto()

#reads a cmd and option X, Y, S and F
GRBL_REGEX = """\A(?P<cmd>\S+)\s*(X(?P<X>-?\d+[.0-9]*)\s*|Y(?P<Y>-?\d+[.0-9]*)\s*|S(?P<S>\d+[.0-9]*)\s*|F(?P<F>\d+[.0-9]*)\s*)*"""
r = re.compile(GRBL_REGEX)


#laser with its coordinates in REAL world (assume MM unit)
class Laser:
    def __init__(self, x=0.0, y=0.0, power=0.0, speed = -1.0) -> None:
        self.X = x
        self.Y = y
        self.Power = power
        self.positionsCalculation = PositionsCalculation.ABSOLUTE
        self.speed = speed

    def fromLaser(template:"Laser") -> "Laser":
        newLaser = Laser()
        newLaser.X = template.X
        newLaser.Y = template.Y
        newLaser.Power = template.Power
        newLaser.positionsCalculation = template.positionsCalculation
        newLaser.speed = template.speed
        return newLaser


    def __str__(self) -> str:
        return f"X={self.X}, Y={self.Y}, Power={self.Power}, Calculations={self.positionsCalculation.name}, Speed={str(self.speed) if self.speed > 0 else 'unknown'}"
    
    #Get the positions IN THE IMAGE of the laser
    def toImageXY(self, xoffset:int = 0, yoffset:int = 0):
        return (self.X * PIXELS_PER_MM + xoffset, self.Y * PIXELS_PER_MM + yoffset)

    def powerOn(self):      
        #reminder power is [0..100] 
        return self.Power > 0.1


#size of a job in mm, estimated time, etc.
class JobStats:
    def __init__(self, name) -> None:
        self.pointFromMM = [100000000000,100000000000]
        self.pointToMM = [-1,-1]
        self.estimatedDurationSec = -1
        self.name = name

    def updateStats (self, laser: Laser, newlaser: Laser):        
        if laser.X == laser.Y == 0:
            #ignore unassigned laser pos assuming you will never reach 0,0.
            return 
        
        #update the duration from distance
        if laser.speed > 0:
            #need a known speed to calculate the duration
            dist = math.sqrt((laser.X - newlaser.X)**2 + (laser.Y - newlaser.Y)**2) 
            #time increment in SECONDS for that move
            #don't care of the mode of the units (mm/min or inches/min), we just need to know the time it takes to go from A to B and since X/Y are in whatever unit you use, the units cancel each other leaving time only
            timeincrement = dist / (newlaser.speed / 60.0)
            #accumulate
            self.estimatedDurationSec += timeincrement

        #update the bounding box
        if laser.X < self.pointFromMM[0]:
            self.pointFromMM[0] = laser.X
        if laser.Y < self.pointFromMM[1]:
            self.pointFromMM[1] = laser.Y
        if laser.X > self.pointToMM[0]:
            self.pointToMM[0] = laser.X
        if laser.Y > self.pointToMM[1]:
            self.pointToMM[1] = laser.Y

    def __duration2String(self) -> str:
        h = self.estimatedDurationSec // 3600
        m = (self.estimatedDurationSec % 3600) // 60
        s = self.estimatedDurationSec % 60        
        return f"{int(h)}h {int(m)}m {int(s)}s"

    def __str__(self) -> str:
        return f"Job '{self.name}' from [{self.pointFromMM[0]:0.2f},{self.pointFromMM[1]:0.2f}]mm ({self.__coord2String(self.physicalCoord2Pixels(self.pointFromMM))} px) to [{self.pointToMM[0]:0.2f},{self.pointToMM[1]:0.2f}]mm ({self.__coord2String(self.physicalCoord2Pixels(self.pointToMM))} px). Area = {self.jobAreaInMM()}.Estimated duration [{self.__duration2String()}] ."
    
    def physicalCoord2Pixels(self, XYinMM):
        #invert Y axis since the image is upside down, so WRONG if you look at it now but since you have to flip the image to use it later...
        return (int(math.ceil(XYinMM[0] * PIXELS_PER_MM)), int((AREA_H_MM - XYinMM[1]) * PIXELS_PER_MM))
    
    def __coord2String(self, XYinMM):
        return f"({int(XYinMM[0])}, {int(XYinMM[1])})"
    
    def jobAreaInMM(self):
        return (self.pointToMM[0] - self.pointFromMM[0], self.pointToMM[1] - self.pointFromMM[1])



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

    if match.group("F") != None:
        #set laser speed in *UNITS PER MINUTE*
        l.speed = float(match.group("F"))


def getColorWithAlpha (color, power, noblending = NO_BLENDING):
    if noblending:
        return color
    
    #power is [0..100] so convert to [0..255]
    return (color[0], color[1], color[2], int(power / 100.0 * 255.0))


def processFile(filepath:str, targetImage:Image = None, xoffset:int = 0, yoffset:int = 0, color="red", lineWidth:float=2, bg_color=BG_COLOR, noblending = NO_BLENDING):
    """ Based on a GRBL file content, generates an Image.
    Not every GRBL commands are supported so go ahead and test, fix, contribute.

    The image will be UPSIDE DOWN so remember to flip it (img = img.transpose(Image.FLIP_TOP_BOTTOM))

    :param filepath: FULL PATH to the source GRBL file
    :param targetImage: provide an image to write into, or function will make one based on the PIXELS_PER_MM, AREA_W_MM and AREA_H_MM
    :param xoffset: if you need to write in the image shifted by x pixels (default 0)
    :param yoffset: if you need to write in the image shifted by y pixels (default 0)
    :param color: which color you want the line, ie : "red" or (0,0,255,128) for semi-transparent blue (default "red")
    :param lineWidth: which width you want the line (default 2)
    :param bg_color: which color you want the background (default BG_COLOR)
    :param noblending: if True, the laser power will be ignored and the line will be drawn without alpha blending (ON/OFF mode) (default False=NO_BLENDING)

    
    """
    laser = Laser()

    contents = None
    with open(filepath, "r") as f:
        contents = f.readlines()

    stats = JobStats(os.path.basename(filepath))


    #img is a calque we'll be drawing on
    calque = Image.new("RGBA", (AREA_H_MM * PIXELS_PER_MM, AREA_W_MM * PIXELS_PER_MM), (255,255,255,0))

    draw = ImageDraw.Draw(calque, "RGBA")

    #convert color to RGBA ("blue" => (0,0,255,255))
    K = ImageColor.getrgb(color)
        
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

            newlaser = Laser.fromLaser(laser)

            __processLine(laser, match=m)

            #Update the stats
            stats.updateStats(laser, newlaser)

        #------------------------ G1 : move (and trace) -------------------------
        elif m.group("cmd") == "G1":
            #newlaser Power is same as previous by default (so continue what you were doing in sort)
            newlaser = Laser.fromLaser(laser)

            #sometimes when filling G1 is used as a G0 depending on the S value
            if m.group("S") != None:                
                #if S is 0, it's a move without power.
                #Convert power to percentage [0..100] (in the file it's per thousand)
                newlaser.Power = float(m.group("S")) / 10.0

            __processLine(newlaser, match=m)


            #Draw a line?
            if newlaser.powerOn():
                draw.line((laser.toImageXY(xoffset, yoffset), newlaser.toImageXY(xoffset, yoffset)), fill=getColorWithAlpha(K, newlaser.Power, noblending), width=lineWidth)

            #Update the stats
            stats.updateStats(laser, newlaser)

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
    

    #make a (default white) background and paste the drawing calque on it
    if targetImage == None:
        background = Image.new("RGBA", (AREA_H_MM * PIXELS_PER_MM, AREA_W_MM * PIXELS_PER_MM), bg_color)
    else:
        background = targetImage.copy()
    background.paste(calque, (0,0), calque)

    #finished
    return background, stats
