## Heavy modification of writevmf for using 
## displacements instead of brushes with different heights

import os
import array
import math
import time

# using BHSPitMonkey's Python vmflib: http://github.com/BHSPitMonkey/vmflib
# Even though it is for Python 3 and above, most of 
# its main features work on Python 2.7 (As of this moment, 18th January, 2014)
import lib.vmflib as vmflib
import lib.vmflib.tools as tools

try:
    from PIL import Image # Uses Pillow to draw a graphic representation of the map
    pillow_installed = True
except:
    pillow_installed = False

from read_w3e import ReadW3E
from lib.dataTypes import QuadBlobs, Bytemap
from lib.helperFunctions import make_number_divisible_by_n, map_list_with_vertex

    
if __name__ == "__main__":
    print "Starting..."
    initTime = time.clock()
    data = ReadW3E("input/war3map.w3e")
    
     
    
    print "Original map dimension: xsize: {0}, ysize: {1}".format(data.mapInfo["width"], data.mapInfo["height"])
    
    m = vmflib.vmf.ValveMap()
    m.world.skyname = "sky_dotasky_01"
    
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
    #xOffset_real = 0
    #yOffset_real = 0
    
    xOffset = (xSize//2)
    yOffset = (ySize//2)
    #xOffset = 0
    #yOffset = 0
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
    #blobAffinity = Bytemap(data.mapInfo["width"], data.mapInfo["height"])
        
        
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
    
    #choice = ("nature/dirt_grass_00", "nature/blendrockground002")
    choice = ("brick/brick_ext_07", "brick/brick_ext_06")
    
    print "Time taken for initialization: {0}".format(time.clock()-initTime)
    
    creationTime = time.clock()
    
    for ix in xrange(xSize//4):
        for iy in xrange(ySize//4):
            
            
            blob = Blockgroups.addBlob(ix, iy)
            
            for iix in xrange(4):
                newX = (ix*4)+iix
                for iiy in xrange(4):
                    newY = (iy*4)+iiy
                    
                    if newX >= data.mapInfo["width"] or newY >= data.mapInfo["height"]:
                        break
                    else:
                        currentHeight = heightmap.getVal(newX, newY)
                        
                        """## We do very simple data interpolation using the heights of the
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
                        Blockgroups.changeTile(newX, newY, tile)"""
                        
                        ## A more simple displacement test that uses the tile height for all points
                        ## of the tile.
                        #tile = Blockgroups.getTile(ix, iy, iix, iiy)
                        #currentVals = tile.getValGroup()
                        if iix > 1: xoffset = 1
                        else: xoffset = 0
                        
                        if iiy > 1: yoffset = 1
                        else: yoffset = 0
                        
                        """for point in currentVals:
                            local_x, local_y, height = point
                            
                            tile.setVal(local_x, local_y, currentHeight*16)
                        
                        Blockgroups.changeTile(ix, iy, iix, iiy, tile)"""
                        
                        for point in blob.getValGroup_iter((iix*4+xoffset, iiy*4+yoffset),
                                                           ((iix+1)*4+xoffset, (iiy+1)*4+yoffset)):
                            local_x, local_y, height = point
                            
                            blob.setVal(local_x, local_y, currentHeight*16)
            
            Blockgroups.sewTilesTogether(ix, iy)
            
            #blob = Blockgroups.getBlob(ix, iy)
          
            
            
    for ix in xrange(xSize//4):
        for iy in xrange(ySize//4):
            height = 64
            vert = vmflib.types.Vertex((ix*4*64)-xOffset_real+2*64, (iy*4*64)-yOffset_real+2*64, 0+(height//2))
            block = tools.Block(origin = vert, dimensions=(4*64, 4*64, height))
            
            ## We alternate between two types of textures. This results in a checkered pattern, 
            ## similar to chess. It is very easy to see where a block starts and ends.
            block.set_material(choice[(iy+ix*(xSize//4))%2])
            #block.set_material("brick/brick_ext_07")
            
            Blockgroups.sew_brush_neighbours(ix, iy)
            blob = Blockgroups.getBlob(ix, iy)
            
            distances_list = []
            for rowNumber in xrange(17):
                row = blob.getRow(rowNumber)
                row = row.tolist()
                #row.reverse()
                distances_list.append(row)
                #row = map(map_list_with_vertex, row)
                #print row
            
            """distances_list = [[64 for i in xrange(17)]]
            for columnNumber in xrange(16):
                #column = blob.getColumn(columnNumber)
                ##column = column.tolist()
                ##colum.reverse()
                #distances_list.append(column)
                column = [64]
                for i in range(4):
                    column.extend([i*32, i*32, i*32, i*32])
                distances_list.append(column)"""
               
            
           #dispInfo = vmflib.brush.DispInfo(4, normals_list, distances_list)
            
            
            #dispInfo.set_startPosition((ix*4*64)-xOffset_real+0*64, (iy*4*64)-yOffset_real+0*64, 0+(height))
            
            #block.top().children.append(dispInfo)
            block.top().set_dispInfo(4, normals_list, distances_list)
            
            m.world.children.append(block)
            
    #scaled_lowestHeight = lowestHeight*64
    #print("The lowest height found is "+str(lowestHeight))
    #print("which after scaling, is "+str(scaled_lowestHeight))
    
    scaled_lowestHeight = 16 # Placeholder value for now
    
    
    # We create a floor and mark it with a different texture
    orig = vmflib.types.Vertex(0,0, 0-scaled_lowestHeight//2)
    floor = tools.Block(origin = orig, dimensions=(xSize_real, ySize_real, scaled_lowestHeight))
    floor.set_material("nature/dirtfloor012a")
    
    m.world.children.append(floor)
    print "Building map finished."
    print "Time taken for map building: {0}".format(time.clock()-creationTime)
    

    print "Now saving data with vmflib..."
    vmfTime = time.clock()
    m.write_vmf("output/wmflibtestmap.vmf")
    print "Time taken for vmf file creation: {0}".format(time.clock()-vmfTime)
    
    print "Everything saved."