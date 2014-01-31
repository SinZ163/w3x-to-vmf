## Heavy modification of writevmf for using 
## displacements instead of brushes with different heights

import os
import array

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

class QuadBlobs():
    def __init__(self, maxX, maxY, blobSizeX, blobSizeY):
        self.maxX = maxX
        self.maxY = maxY
        
        self.blobSizeX = blobSizeX
        self.blobSizeY = blobSizeY
        
        self.blobmap = [False for i in xrange(maxX*maxY)]
    
    def addBlob(self, x, y, height):
        index = y * self.maxX + x
        
        bloblist = [0 for i in xrange(self.blobSizeX*self.blobSizeY)]
        
        self.blobmap[index] = bloblist
    
    def getBlob(self, x, y):
        index = y * self.maxX + x
        
        return self.blobmap[index]
    
    def getTile(self, big_x, big_y):
        x, y = big_x//blobSizeX, big_y//blobSizeY
        
    
            
class Bytemap():
    def __init__(self, maxX, maxY):
        self.maxX = maxX
        self.maxY = maxY
        self.map = array.array("h", [-1 for x in xrange(maxX*maxY)])
    
    def setVal(self, x, y, val):
        index = y * self.maxX + x
        self.map[index] = val
    
    def getVal(self, x, y):
        index = y * self.maxX + x
        return self.map[index]
    
    def getValGroup_iter(self, minCoords, maxCoords):
        for ix in xrange(minCoords[0],maxCoords[0]):
            for iy in xrange(minCoords[1],maxCoords[1]):
                yield ix, iy, self.getVal(ix, iy)
                
    def getValGroup(self, minCoords, maxCoords):
        grouplist = []
        for ix in xrange(minCoords[0],maxCoords[0]):
            for iy in xrange(minCoords[1],maxCoords[1]):
                grouplist.append((ix, iy, self.getVal(ix, iy))

## We make a number divisible by n by rounding up. For that, 
## we calculate how much we would have to add to the number for it to
## be divisible without leaving any remains beyond the decimal point.
def make_number_divisible_by_n(num, n):
    if num % n != 0:
        remaining = n - (num % n)
        return num + remaining
    else:
        return num
    

    
    
    
if __name__ == "__main__":
    data = ReadW3E("input/war3map.w3e")
    
    print "Original map dimension: xsize: {0}, ysize: {1}".format(data.mapInfo["width"], data.mapInfo["height"])
    
    m = vmflib.vmf.ValveMap()
    
    # x_factor and y_factor will limit the size of objects that are drawn, if the map should be smaller
    # Remains from a different program, might be removed in future revisions
    x_factor = 1
    y_factor = 1
    
    # size of original map and an estimated height. The height value is set to an artificial size
    xSize, ySize, height = (data.mapInfo["width"]//x_factor), (data.mapInfo["height"]//y_factor), 2500
    
    xSize = make_number_divisible_by_n(xSize, 4)
    ySize = make_number_divisible_by_n(ySize, 4)
    
    print "Adjusted values for map dimension: xsize: {0}, ysize: {1}".format(xSize,ySize)
        
    
    # size of the resulting source map. At the moment, changing the scaling requires 
    # changing the constant in other places in the code 
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
    
    
    bloblist = []
    
    heightmap = Bytemap(data.mapInfo["width"], data.mapInfo["height"])
    blobAffinity = Bytemap(data.mapInfo["width"], data.mapInfo["height"])
        
        
    # Iterate once over the map to store the height of each tile.
    # This way, we avoid having to use the binary AND every time 
    # we try to retrieve the height of a tile
    
    #lowestHeight = 10000000
    
    for x in xrange(data.mapInfo["width"]):
        for y in xrange(data.mapInfo["height"]):
            index = y*data.mapInfo["width"] + x
            tile = data.mapInfo["info"][index]
            
            height = tile["nibble2"] & 0xF
            
            ## voodoo magic, disabled for now until I understand it
            #The tilepoint "final height" you see on the WE is given by:
            #(ground_height - 0x2000 + (layer - 2)*0x0200)/4
            #height = tile["groundHeight"] - 0x2000 + ((tile["nibble2"] & 0xF) -2) *0x0200 / 4
            #if height < lowestHeight:
            #    lowestHeight = height
    
            heightmap.setVal(x, y, height)
    
    for ix in xrange(xSize//4):
        for iy in xrange(ySize//4):
            height = 64
            vert = vmflib.types.Vertex((ix*4*64)-xOffset_real+2*64, (iy*4*64)-yOffset_real+2*64, 0+(height//2))
            block = tools.Block(origin = vert, dimensions=(4*64, 4*64, height))
            
            block.set_material("brick/brick_ext_07")
            vmflib.brush.DispInfo
            
            m.world.children.append(block)
            
    #scaled_lowestHeight = lowestHeight*64
    #print("The lowest height found is "+str(lowestHeight))
    #print("which after scaling, is "+str(scaled_lowestHeight))
    
    scaled_lowestHeight = 16 # Placeholder value for now
    
    
    # We create a floor and mark it with a different brick texture
    orig = vmflib.types.Vertex(0,0, 0-scaled_lowestHeight//2)
    floor = tools.Block(origin = orig, dimensions=(xSize_real, ySize_real, scaled_lowestHeight))
    floor.set_material("brick/brick_ext_06")
    
    m.world.children.append(floor)
    print "Building map finished."
    
    
    print "Now saving data with vmflib..."
    m.write_vmf("output/wmflibtestmap.vmf")
    
    
    
    print "Everything saved."