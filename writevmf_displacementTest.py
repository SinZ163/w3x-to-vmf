## Heavy modification of writevmf for using 
## displacements instead of brushes with different heights

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

class QuadBlobs():
    def __init__(self, maxX, maxY, blobSizeX, blobSizeY):
        self.maxX = maxX
        self.maxY = maxY
        
        self.blobSizeX = blobSizeX
        self.blobSizeY = blobSizeY
        
        self.blobmap = [False for i in xrange(maxX*maxY)]
    
    def addBlob(self, x, y):
        index = y * self.maxX + x
        
        blob = Bytemap(self.blobSizeX**2+1, self.blobSizeY**2+1)
        
        self.blobmap[index] = blob
    
    def getBlob(self, x, y):
        index = y * self.maxX + x
        
        return self.blobmap[index]
    
    def getTile(self, big_x, big_y):
        x, y = big_x//self.blobSizeX, big_y//self.blobSizeY
        
        local_x, local_y = big_x % self.blobSizeX, big_y % self.blobSizeY
        
        
        
        if local_x > 1: x_offset = 1
        else: x_offset = 0
        
        if local_y > 1: y_offset = 1
        else: y_offset = 0
        
        local_x = local_x * self.blobSizeX
        local_y = local_y * self.blobSizeY
        
        tiledata = self.getBlob(x, y).getSubBlob((local_x+x_offset, local_y+y_offset), 
                                                 (local_x+x_offset+self.blobSizeX, local_y+y_offset+self.blobSizeY))
        
        return tiledata
    
    def changeTile(self, big_x, big_y, tile):
        x, y = big_x//self.blobSizeX, big_y//self.blobSizeY
        
        local_x, local_y = big_x % self.blobSizeX, big_y % self.blobSizeY
        
        #local_x = local_x * self.blobSizeX
        #local_y = local_y * self.blobSizeY
        
        if local_x > 1: x_offset = 1
        else: x_offset = 0
        
        if local_y > 1: y_offset = 1
        else: y_offset = 0
        
        blob = self.getBlob(x, y)
        
        local_x = local_x * self.blobSizeX
        local_y = local_y * self.blobSizeY
        
        blob.setValGroup_fromBlob(tile, (local_x+x_offset, local_y+y_offset), 
                                  (local_x+x_offset+self.blobSizeX, local_y+y_offset+self.blobSizeY))
    
    ## If you have noticed it, we use offsets to skip one row of data in the middle
    ## of the blob. As a result, at x = 8 and y = 8 in the tile there will be a steep step down,
    ## because there is no data. We will fix this using average data.
    def sewTilesTogether(self, x, y):
        blob = self.getBlob(x, y)
        midX, midY = 8, 8
        
        y = midY
        for x in range(17):
            if x == midX:
                pass
            else:
                up, down =  blob.getVal(x, y+1), blob.getVal(x, y-1)
                blob.setVal(x, y, (up + down) // 2)
        
        x = midX
        for y in range(17):
            if y == midY:
                pass
            else:
                left, right =  blob.getVal(x+1, y), blob.getVal(x-1, y)
                blob.setVal(x, y, (left + right) // 2)
        
        
        up, down, left, right = blob.getVal(midX, midY+1), blob.getVal(midX, midY-1), blob.getVal(midX+1, midY), blob.getVal(midX-1, midY)
        middleHeight = (up+down+left+right) // 4
        
        blob.setVal(midX, midY, middleHeight)
        
        
        
            
            
        
        
    
            
class Bytemap():
    def __init__(self, maxX, maxY, init = -1, initArray = None):
        self.maxX = maxX
        self.maxY = maxY
        
        if initArray == None:
            self.map = array.array("h", [init for x in xrange(maxX*maxY)])
        else:
            self.map = array.array("h", initArray)
            
    def setVal(self, x, y, val):
        index = y * self.maxX + x
        self.map[index] = val
    
    def getVal(self, x, y):
        index = y * self.maxX + x
        if x < 0 or y < 0 or x >= self.maxX or y >= self.maxY:
            raise RuntimeError("Coordinates are out of range: x: {0}, y: {1}, maxX: {2}, maxY: {3}".format(x,y, self.maxX, self.maxY))
        return self.map[index]
    
    ## To avoid blocks of try:except for checking if the index is out of range,
    ## we just use a special function which checks if the index is in range or not.
    ## If it isn't, it will return a placeholder value
    def getVal_tolerant(self, x, y):
        index = y * self.maxX + x
        if x < 0 or y < 0 or x >= self.maxX or y >= self.maxY:
            return False
        else:
            return self.map[index]
    
    def getValGroup_iter(self, minCoords = (0,0), maxCoords = "max"):
        
        ## Can't do this when defining arguments at the same time as the function,
        ## so we have to do initiate it like this.
        if maxCoords == "max":
            maxCoords = (self.maxX, self.maxY) 
                    
            
        
        
        for iy in xrange(minCoords[1],maxCoords[1]):
            for ix in xrange(minCoords[0],maxCoords[0]):
                yield ix, iy, self.getVal(ix, iy)
                
    def getValGroup(self, minCoords = (0,0), maxCoords = "max", noCoordinates = False):
        if maxCoords == "max":
            maxCoords = (self.maxX, self.maxY) 
            
        grouplist = []
        for ix in xrange(minCoords[0],maxCoords[0]):
            for iy in xrange(minCoords[1],maxCoords[1]):
                if noCoordinates:
                    grouplist.append(self.getVal(ix, iy))
                else:
                    grouplist.append((ix, iy, self.getVal(ix, iy)))
        
        return grouplist
             
    def setValGroup_fromBlob(self, blob, minCoords, maxCoords):
        for iy in xrange(minCoords[1],maxCoords[1]):
            for ix in xrange(minCoords[0],maxCoords[0]):
                miniX, miniY = ix - minCoords[0], iy - minCoords[1]
                self.setVal(ix, iy, blob.getVal(miniX, miniY))
             
    
    def getSubBlob(self, minCoords, maxCoords):
        x, y = maxCoords[0] - minCoords[0], maxCoords[1] - minCoords[1]
        
        subBlobList = self.getValGroup(minCoords, maxCoords, True)
        
        return Bytemap(x, y, 0, subBlobList)
    
    def getRow(self, rowNum):
        index = y * self.maxX + x
        
        start = rowNum * self.maxX
        end = rowNum * self.maxX + self.maxX
        
        return self.map[start:end]

class TileMap(Bytemap):
    def __init__(self, *args):
        self.__init__(*args)
    
## We make a number divisible by n by rounding up. For that, 
## we calculate how much we would have to add to the number for it to
## be divisible without leaving any remains beyond the decimal point.
def make_number_divisible_by_n(num, n):
    if num % n != 0:
        remaining = n - (num % n)
        return num + remaining
    else:
        return num

## A helper function which will be used with map()
## on a list of height values to create normals.
def map_list_with_vertex(height):
    return vmflib.types.Vertex(0,0, height)
    

    
if __name__ == "__main__":
    print "Starting..."
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
    
            heightmap.setVal(x, y, height*10)
    
    Blockgroups = QuadBlobs(xSize//4, ySize//4, 4, 4)
    
    ## We initialize distance values which will be used for 
    ## height interpolation.
    local_upPosition = 5
    local_downPosition = -1
    local_leftPosition = -1
    local_rightPosition = 5
    
    ## For the moment, we will not do anything interesting with normals.
    ## We will set it to 0,0,1 i.e. the normal vector will point straight upwards.
    normals_row = [vmflib.types.Vertex(0,0,1) for i in xrange(17)]
    normals_list = [normals_row for i in xrange(17)]
    
    choice = ("brick/brick_ext_07", "brick/brick_ext_06")
    
    for ix in xrange(xSize//4):
        for iy in xrange(ySize//4):
            height = 64
            vert = vmflib.types.Vertex((ix*4*64)-xOffset_real+2*64, (iy*4*64)-yOffset_real+2*64, 0+(height//2))
            block = tools.Block(origin = vert, dimensions=(4*64, 4*64, height))
            
            ## We alternate between two types of textures. This results in a checkered pattern, 
            ## similar to chess. It is very easy to see where a block starts and ends.
            block.set_material(choice[(iy+ix*(xSize//4))%2])
            #block.set_material("brick/brick_ext_07")
            
            Blockgroups.addBlob(ix, iy)
            
            
            
            for iix in xrange(4):
                for iiy in xrange(4):
                    newX = (ix*4)+iix
                    newY = (iy*4)+iiy
                    
                    if newX >= data.mapInfo["width"] or newY >= data.mapInfo["width"]:
                        break
                    else:
                        currentHeight = heightmap.getVal(newX, newX)
                        
                        ## We do very simple data interpolation using the heights of the
                        ## 4 neighbours of a tile.
                        neighbourUp     =   heightmap.getVal_tolerant(newX, newY+1) or currentHeight
                        neighbourDown   =   heightmap.getVal_tolerant(newX, newY-1) or currentHeight
                        neighbourLeft   =   heightmap.getVal_tolerant(newX-1, newY) or currentHeight
                        neighbourRight  =   heightmap.getVal_tolerant(newX+1, newY) or currentHeight
                        
                        #tile = blob.getSubBlob((iix, iiy), (iix+4, iiy+4))
                        tile = Blockgroups.getTile(newX, newY)
                        
                        
                        currentVals = tile.getValGroup()
                        
                        for point in currentVals:
                            local_x, local_y, height = point
                            
                            upDist = abs(local_y - local_upPosition)
                            downDist = abs(local_y - local_downPosition)
                            
                            leftDist = abs(local_x - local_leftPosition)
                            rightDist = abs(local_x - local_rightPosition)
                            
                            
                            tile.setVal(local_x, local_y, int(math.floor( ((1.0/upDist) * neighbourUp
                                                             + (1.0/downDist) * neighbourDown
                                                             + (1.0/leftDist) * neighbourLeft
                                                             + (1.0/rightDist) * neighbourRight) 
                                                            
                                                             + upDist * currentHeight
                                                             + downDist * currentHeight
                                                             + leftDist * currentHeight
                                                             + rightDist * currentHeight)))
                        Blockgroups.changeTile(newX, newY, tile)
                        
                        ## A more simple displacement test that uses the tile height for all points
                        ## of the tile.
                        """tile = Blockgroups.getTile(newX, newY)
                        currentVals = tile.getValGroup()
                        
                        for point in currentVals:
                            local_x, local_y, height = point
                            
                            tile.setVal(local_x, local_y, currentHeight)
                        
                        Blockgroups.changeTile(newX, newY, tile)"""
            
            Blockgroups.sewTilesTogether(ix, iy)
            
            blob = Blockgroups.getBlob(ix,iy)
            
          
            distances_list = []
            
            for rowNumber in xrange(17):
                row = blob.getRow(rowNumber)
                distances_list.append(row.tolist())
                #row = map(map_list_with_vertex, row)
                #print row
                
            
            dispInfo = vmflib.brush.DispInfo(4, normals_list, distances_list)
            
            block.top().children.append(dispInfo)
            
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