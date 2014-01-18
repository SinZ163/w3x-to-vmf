import traceback
import re
import os
import array
import math

# using BHSPitMonkey's Python vmflib: http://github.com/BHSPitMonkey/vmflib
# Even though it is for Python 3 and above, most of 
# its main features work on Python 2.7 (As of this moment, 18th January, 2014)
import vmflib
import vmflib.tools as tools

try:
    from PIL import Image # Uses Pillow to draw a graphic representation of the map
    pillow_installed = True
except:
    pillow_installed = False

from read_w3e import ReadW3E

#def subInfo(template, id, x, x2, y, y2, z):
#    toWrite = re.sub("~~ID~~", str(id), template)
#    toWrite = re.sub("~~X~~", str(x), toWrite)
#    toWrite = re.sub("~~X2~~", str(x2), toWrite)
#    toWrite = re.sub("~~Y~~", str(y), toWrite)
#    toWrite = re.sub("~~Y2~~", str(y2), toWrite)
#    toWrite = re.sub("~~Z~~", str(z), toWrite)
#    
#    return toWrite
    
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
#vmfTemplate = {}

#for fileName in ["header","footer","planeEntry"]:
#    with open("template/"+fileName+".txt", "r") as f:
#        vmfTemplate[fileName] = f.read()

# We use the vmf library to create a map for the source engine
m = vmflib.vmf.ValveMap()

# x_factor and y_factor will limit the size of objects that are drawn, if the map should be smaller
# Remains from a different program, might be removed in future revisions
x_factor = 1
y_factor = 1

# size of original map and an estimated height
xSize, ySize, height = (data.mapInfo["width"]//x_factor), (data.mapInfo["height"]//y_factor), 2500
# size of the resulting source map
xSize_real, ySize_real = xSize*64, ySize*64

# The offset variables are used to move the created brushes in such a way
# so that the middle of the wc3 map is the (0,0) coordinate in the vmf file
xOffset_real = xSize_real//2
yOffset_real = ySize_real//2

xOffset = (xSize//2)
yOffset = (ySize//2)
zOffset = (height//2)



orig = vmflib.types.Vertex(0,0-yOffset_real, 0+zOffset)
skybox_back = tools.Block(origin = orig, dimensions=(xSize_real, 8, height))
skybox_back.set_material("tools/toolsskybox")

orig = vmflib.types.Vertex(0,0+yOffset_real, 0+zOffset)
skybox_front = tools.Block(origin = orig, dimensions=(xSize_real, 8,height))
skybox_front.set_material("tools/toolsskybox")

orig = vmflib.types.Vertex(0-xOffset_real,0, 0+zOffset)
skybox_left = tools.Block(origin = orig, dimensions=(8, ySize_real,height))
skybox_left.set_material("tools/toolsskybox")

orig = vmflib.types.Vertex(0+xOffset_real,0, 0+zOffset)
skybox_right = tools.Block(origin = orig, dimensions=(8, ySize_real,height))
skybox_right.set_material("tools/toolsskybox")

orig = vmflib.types.Vertex(0,0, 0+zOffset*2)
skybox_ceiling = tools.Block(origin = orig, dimensions=(xSize_real, ySize_real, 8))
skybox_ceiling.set_material("tools/toolsskybox")


m.world.children.append(skybox_back)
m.world.children.append(skybox_front)
m.world.children.append(skybox_left)
m.world.children.append(skybox_right)
m.world.children.append(skybox_ceiling)


print "Done adding walls, now to do the map itself..." 

try:
    os.makedirs('./output')
    print "created output directory"
except OSError as error:
    print str(error)

with open("output/output.vmf", "w") as f:
    #f.write(vmfTemplate["header"])
    
    bloblist = []
    
    heightmap = Bytemap(data.mapInfo["width"], data.mapInfo["height"])
    blobAffinity = Bytemap(data.mapInfo["width"], data.mapInfo["height"])
    
    ## Debug heatmap, used to check how often a single pixel has been drawn.
    ## It is used to create an image, check code at the far bottom of this file
    #debug_heatmap = Bytemap(data.mapInfo["width"], data.mapInfo["height"])
    
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
                if heightmap.getVal(x, y) == neededHeight and blobAffinity.getVal(x, y) == -1:
                    pass
                else:
                    # Damnit Python, why is there no built-in way to break out
                    # of multiple loops? :(
                    if x > startX:
                        do_break = True
                    else:
                        y_limit = y
                    break
                
            if do_break == True:
                x_limit = x
                break
                    
        return (x_limit, y_limit)
        
        
    # Iterate once over the map to store the height of each tile.
    # This way, we avoid having to use the binary AND every time 
    # we try to retrieve the height of a tile
    
    #lowestHeight = 10000000
    
    for x in xrange(data.mapInfo["width"]):
        for y in xrange(data.mapInfo["height"]):
            
            index = y*data.mapInfo["height"] + x
            tile = data.mapInfo["info"][index]
            
            height = tile["nibble2"] & 0xF
            
            ## voodoo magic, disabled for now until I understand it
            #The tilepoint "final height" you see on the WE is given by:
            #(ground_height - 0x2000 + (layer - 2)*0x0200)/4
            #height = tile["groundHeight"] - 0x2000 + ((tile["nibble2"] & 0xF) -2) *0x0200 / 4
            #if height < lowestHeight:
            #    lowestHeight = height

            heightmap.setVal(x, y, height)
    
    #scaled_lowestHeight = lowestHeight*64
    #print("The lowest height found is "+str(lowestHeight))
    #print("which after scaling, is "+str(scaled_lowestHeight))
    
    scaled_lowestHeight = 16 # Placeholder value for now
    
    # We create a floor and mark it with a different brick texture
    # (brick_ext_06 instead of brick_ext_07)
    orig = vmflib.types.Vertex(0,0, 0-scaled_lowestHeight//2)
    floor = tools.Block(origin = orig, dimensions=(xSize_real, ySize_real, scaled_lowestHeight))
    floor.set_material("brick/brick_ext_06")
    
    m.world.children.append(floor)
    print "Created floor at z={0}".format(0-scaled_lowestHeight//2)
    
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
        startCoords, endCoords, height = plane
        
        startX, startY = startCoords
        endX, endY = endCoords
        
        ## We scale the planes up by a factor of 16 <- OUTDATED INFO
        #f.write(subInfo(vmfTemplate["planeEntry"], index, startX*16, endX*16, startY*16, endY*16, height*16))
        
        # We scale the blocks up by a factor of 64
        boxWidth = endX-startX+1
        boxLength = endY-startY+1
        height = (height)*64
        
        midX = (startX+endX) // 2
        midY = (startY+endY) // 2
        
        # A little bit of optimization, only draw the block if it has a non-zero height
        # (Hammer only likes blocks with non-zero dimensions, for good reason)
        if height > 0:
            vert = vmflib.types.Vertex((midX*64)-xOffset_real,(midY*64)-yOffset_real, 0+(height//2))
            block = tools.Block(origin = vert, dimensions=(boxWidth*64, boxLength*64, height))
            block.set_material("brick/brick_ext_07")
            
            m.world.children.append(block)
        
        ## DEBUG CODE TO CHECK THE MAP FOR OVERLAPPING FIELDS
        #for ix in xrange(startX, endX):
        #    for iy in xrange(startY, endY):
        #        curr = debug_heatmap.getVal(ix, iy)
        #        if curr == -1:
        #            curr = 1
        #        else:
        #            curr = curr+1
        #        debug_heatmap.setVal(ix, iy, curr)
        
        # We create an image on which the planes are drawn. 
        # Same color = same plane, but due to the high amount of planes some might have similar colors
        # We calculate the RGB values using a bit of modulus to make the value fit the byte range of the R, G and B values of a color
        if pillow_installed: img.paste((index%(2**8), index%(2**8), index%(2**16)), (startX*4, startY*4, endX*4, endY*4))
    
    print "Building map finished."
    #f.write(vmfTemplate["footer"])
    if pillow_installed: img.save("output/img.png", "PNG")
    
    print "Now saving data with vmflib..."
    m.write_vmf("output/wmflibtestmap.vmf")
    
    ## Debug code, draws a picture that shows how often a single pixel has been overwritten
    ## Ideally, the entire picture should have the same color, i.e. each pixel has been overwritten only once
    #debugpix = Image.new("L", (data.mapInfo["width"], data.mapInfo["height"]), 255)
    #for ix in range(data.mapInfo["width"]):
    #    for iy in range(data.mapInfo["height"]):
    #        val = debug_heatmap.getVal(ix, iy)
    #        if val < 0: print val
    #        debugpix.putpixel((ix, iy), val*40)
    #
    #debugpix.save("output/heatmap.png", "PNG")
    
    print "Everything saved."