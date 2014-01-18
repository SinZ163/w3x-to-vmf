import traceback
import re
import os
import array
import math

try:
    from PIL import Image # Uses Pillow to draw a graphic representation of the map
    pillow_installed = True
except:
    pillow_installed = False

from read_w3e import ReadW3E

def subInfo(template, id, x, x2, y, y2, z, z2):
    toWrite = re.sub("~~ID~~", str(id), template)
    toWrite = re.sub("~~X~~", str(x), toWrite)
    toWrite = re.sub("~~X2~~", str(x2), toWrite)
    toWrite = re.sub("~~Y~~", str(y), toWrite)
    toWrite = re.sub("~~Y2~~", str(y2), toWrite)
    toWrite = re.sub("~~Z~~", str(z), toWrite)
    toWrite = re.sub("~~Z2~~", str(z2), toWrite)
    return toWrite
    
class Bytemap():
    def __init__(self, maxX, maxY):
        self.maxX = maxX
        self.maxY = maxY
        self.map = array.array("h", [-1 for x in xrange(maxX*maxY)])
    
    def setVal(self, x, y, val):
        index = y * self.maxY + x
        self.map[index] = val
    
    def getVal(self, x, y):
        index = y * self.maxY + x
        return self.map[index]

data = ReadW3E("input/war3map.w3e")

mapInfo = ""
vmfTemplate = {}

for fileName in ["header","footer","planeEntry","brushHeader","brushFooter"]:
    with open("template/"+fileName+".txt", "r") as f:
        vmfTemplate[fileName] = f.read()

try:
    os.makedirs('./output')
    print "created output directory"
except OSError as error:
    print str(error)

with open("output/output.vmf", "w") as f:
    brushCount = 0
    f.write(vmfTemplate["header"])
    bloblist = []
    
    heightmap = Bytemap(data.mapInfo["width"], data.mapInfo["height"])
    blobAffinity = Bytemap(data.mapInfo["width"], data.mapInfo["height"])
    
    
    if pillow_installed: img = Image.new("RGB", (data.mapInfo["width"]*4, data.mapInfo["height"]*4))
    
    # rectangularCheck uses a sort of brute force approach to group planes together
    # We travel along the y axis until we find a tile that has a different height than
    # the neededHeight value specifies. On the first iteration of the y axis we
    # set the maximum y coordinate of the plane.
    # If x is bigger than the starting coordinate and we encounter a tile with a
    # different height, we break out of both for loops and set the maximum x coordinate
    # of the plane and return both maximums.
    def rectangularCheck(startX, startY, neededHeight):
        do_break = False
        
        x_limit = data.mapInfo["width"]
        y_limit = data.mapInfo["height"]
        
        for x in xrange(startX, x_limit):
            for y in xrange(startY, y_limit):
                if heightmap.getVal(x, y) == neededHeight:
                    pass
                else:
                    # Damnit Python, why is there no built-in way to break out
                    # of multiple loops? :(
                    if x > startX:
                        do_break = True
                    else:
                        y_limit = y - 1
                    break
                
            if do_break == True:
                x_limit = x-1
                break
                    
        return (x_limit, y_limit)
        
    # Iterate once over the map to store the height of each tile.
    # This way, we avoid having to use the binary AND every time 
    # we try to retrieve the height of a tile
    lowestHeight = 10000000
    for x in xrange(data.mapInfo["width"]):
        for y in xrange(data.mapInfo["height"]):
            
            index = y*data.mapInfo["height"] + x
            tile = data.mapInfo["info"][index]
            #The tilepoint "final height" you see on the WE is given by:
            #(ground_height - 0x2000 + (layer - 2)*0x0200)/4
            height = tile["groundHeight"] - 0x2000 + ((tile["nibble2"] & 0xF) -2) *0x0200 / 4
            if height < lowestHeight:
                lowestHeight = height
            heightmap.setVal(x, y, height)
    print("The lowest height found is "+str(lowestHeight))
    print("which after scaling, is "+str(lowestHeight*16))
    # We iterate a second time to group tiles of similar height together.
    # rectangularCheck uses a brute force approach.
    for x in xrange(data.mapInfo["width"]):
        for y in xrange(data.mapInfo["height"]):
            
            localHeight = heightmap.getVal(x,y)
            
            # We check if the tile already belongs to a group.
            # -1 means no. If not equal to -1, we skip it.
            if blobAffinity.getVal(x, y) == -1:
                endX, endY = rectangularCheck(x, y, localHeight)
                
                for ix in xrange(x, endX):
                    for iy in xrange(y, endY):
                        # We set the value for the coordinates to 1 to signal that
                        # they belong to a "blob", i.e. a group of planes
                        blobAffinity.setVal(ix, iy, 1) 
                
                bloblist.append( ((x,y), (endX, endY), localHeight) )
            
    print "Preparations are done, now creating the planes..."
    
    for index, plane in enumerate(bloblist):
        f.write(re.sub("~~ID~~", str(brushCount),vmfTemplate["brushHeader"]))
        brushCount = brushCount + 1
        
        startCoords, endCoords, height = plane
        
        startX, startY = startCoords
        endX, endY = endCoords
        
        # We scale the planes up by a factor of 16
        #top face
        f.write(subInfo(vmfTemplate["planeEntry"], index*6, startX*16, endX*16, startY*16, endY*16, height*16, height*16))
        #bottom face
        f.write(subInfo(vmfTemplate["planeEntry"], index*6+1, startX*16, endX*16, startY*16, endY*16, lowestHeight*16, lowestHeight*16))
        
        #two faces on the X axis
        f.write(subInfo(vmfTemplate["planeEntry"], index*6+2, startX*16, startX*16, startY*16, endY*16, lowestHeight*16, height*16))
        f.write(subInfo(vmfTemplate["planeEntry"], index*6+3, endX*16, endX*16, startY*16, endY*16, lowestHeight*16, height*16))
        
        #two faces on the Y axis
        f.write(subInfo(vmfTemplate["planeEntry"], index*6+4, startX*16, endX*16, startY*16, startY*16, lowestHeight*16, height*16))
        f.write(subInfo(vmfTemplate["planeEntry"], index*6+5, startX*16, endX*16, endY*16, endY*16, lowestHeight*16, height*16))
        
        # We create an image on which the planes are drawn. 
        # Same color = same plane, but due to the high amount of planes some might have similar colors
        # We calculate the RGB values using a bit of modulus to make the value fit the byte range of the R, G and B values of a color
        if pillow_installed: img.paste((index%(2**8), index%(2**8), index%(2**16)), (startX*4, startY*4, endX*4, endY*4))
        
        f.write(vmfTemplate["brushFooter"])

    print "It is finished."
    f.write(vmfTemplate["footer"])
    if pillow_installed: img.save("output/img.png", "PNG")
    
    print "Everything saved."