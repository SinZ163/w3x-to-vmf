import time

import lib.vmflib as vmflib
import lib.vmflib.tools as tools

from lib.dataTypes import QuadBlobs, Bytemap
from lib.helperFunctions import make_number_divisible_by_n, map_list_with_vertex

class VmfGen():
    def __init__(self, base):
        self.base = base
        self.name = "Displacement VMF"
        self.description = "Displacement-based VMF creation using fixed-size brushes and displacements."
        
        print "{0} initialized".format(self.name)
    
    def create_vmf(self):
        adjusted_WC3xSize = make_number_divisible_by_n(self.base.WC3map_xSize, 4)
        adjusted_WC3ySize = make_number_divisible_by_n(self.base.WC3map_ySize, 4)
        
        wc3_tileSize = self.base.wc3_tileSize
        wc3_tileHeight = self.base.wc3_tileHeight
        
        Blockgroups = QuadBlobs(adjusted_WC3xSize//4, adjusted_WC3ySize//4, 4, 4)
        
        ## For the moment, we will not do anything interesting with normals.
        ## We will set it to 0,0,1 i.e. the normal vector will point straight upwards.
        normals_row = [vmflib.types.Vertex(0,0,1) for i in xrange(17)]
        normals_list = [normals_row for i in xrange(17)]
        
        #choice = ("nature/dirt_grass_00", "nature/blendrockground002")
        choice = ("brick/brick_ext_07", "brick/brick_ext_06")
        
        creationTime = time.clock()
        
        for ix in xrange(adjusted_WC3xSize//4):
            for iy in xrange(adjusted_WC3ySize//4):
                
                blob = Blockgroups.addBlob(ix, iy)
                
                for iix in xrange(4):
                    newX = (ix*4)+iix
                    
                    for iiy in xrange(4):
                        
                        newY = (iy*4)+iiy
                        
                        if newX >= self.base.WC3map_xSize or newY >= self.base.WC3map_xSize:
                            break
                        else:
                            currentHeight = self.base.WC3map_heightmap.getVal(newX, newY)
                            
                            # Is the ramp flag set? If so, we will try to draw a transition between two layers
                            if self.base.WC3map_rampmap.getVal(newX, newY) == 1 and False: # for the moment disabled because of issues
                                pass
                                """upperTile = self.base.WC3map_heightmap.getVal(newX, newY+1)
                                lowerTile = self.base.WC3map_heightmap.getVal(newX, newY-1)
                                leftTile = self.base.WC3map_heightmap.getVal(newX-1, newY)
                                rightTile = self.base.WC3map_heightmap.getVal(newX+1, newY)
                                
                                # The startX and startY variables are coordinates for the points
                                # that are closest to the highest tile
                                startX = 0
                                startY = 0
                                
                                if upperTile < lowerTile: 
                                    startY = 3
                                    directionType = 1
                                elif upperTile > lowerTile:
                                    startY = 0
                                    directionType = 1
                                    
                                elif leftTile < rightTile:
                                    startX = 0
                                    directionType = 2
                                elif leftTile > rightTile:
                                    startX = 3
                                    directionType = 2
                                
                                if iix > 1: xoffset = 1
                                else: xoffset = 0
                                
                                if iiy > 1: yoffset = 1
                                else: yoffset = 0
                                
                                if directionType == 1: # A ramp that goes from top to down along the y axis (or vice versa)
                                    for local_y in xrange(4):
                                        distance = 3 - local_y 
                                        
                                        # Attempt to create a weighed average value for points on the ramp
                                        # Does not appear to work correctly just yet
                                        average = (((local_y+1)/4.0) * lowerTile + ((distance+1)/4.0) * upperTile) / 2.0
                                        for local_x in xrange(4):
                                            average 
                                            blob.setVal(iix*4+local_x+xoffset, iiy*4+local_y+yoffset, average*64)
                                            
                                elif directionType == 2: # A ramp that goes from left to right along the x axis (or vice versa)
                                    for local_x in xrange(4):
                                        distance = 3 - local_x 
                                        average = (((local_x+1)/4.0) * leftTile + ((distance+1)/4.0) * rightTile) / 2.0
                                        for local_y in xrange(4):
                                            blob.setVal(iix*4+local_x+xoffset, iiy*4+local_y+yoffset, average*64)"""
                                """for pointX in xrange(4):
                                    for pointY in xrange(4):
                                        local_x = 
                                for point in blob.getValGroup_iter((iix*4+xoffset, iiy*4+yoffset),
                                                                   ((iix+1)*4+xoffset, (iiy+1)*4+yoffset)):
                                    local_x, local_y, height = point
                                    
                                    blob.setVal(local_x, local_y, currentHeight32)"""
                                
                                
                            else:
                                ## A simple displacement test that uses the tile height for all points
                                ## of the tile.
                                #tile = Blockgroups.getTile(ix, iy, iix, iiy)
                                #currentVals = tile.getValGroup()
                                if iix > 1: xoffset = 1
                                else: xoffset = 0
                                
                                if iiy > 1: yoffset = 1
                                else: yoffset = 0
                                
                                for point in blob.getValGroup_iter((iix*4+xoffset, iiy*4+yoffset),
                                                                   ((iix+1)*4+xoffset, (iiy+1)*4+yoffset)):
                                    local_x, local_y, height = point
                                    
                                    blob.setVal(local_x, local_y, currentHeight*wc3_tileHeight)
                
                # A single displacement map will a row and a column of missing data,
                # going exactly through the middle of the map. We will fill these spots with
                # data from the neighbouring tiles.
                Blockgroups.sewTilesTogether(ix, iy)
        
        vmf_xoffset = self.base.vmfmap_xMidOffset
        vmf_yoffset = self.base.vmfmap_yMidOffset
        
        for ix in xrange(adjusted_WC3xSize//4):
            for iy in xrange(adjusted_WC3xSize//4):
                height = wc3_tileHeight
                vert = vmflib.types.Vertex((ix*4*wc3_tileSize)-vmf_xoffset+2*wc3_tileSize, 
                                           (iy*4*wc3_tileSize)-vmf_yoffset+2*wc3_tileSize, 
                                           (height//2))
                
                block = tools.Block(origin = vert, dimensions=(4*wc3_tileSize, 4*wc3_tileSize, height))
                
                ## We alternate between two types of textures. This results in a checkered pattern, 
                ## similar to chess. It is very easy to see where a block starts and ends.
                block.set_material(choice[(iy+ix*(adjusted_WC3xSize//4))%2])
                #block.set_material("brick/brick_ext_07")
                
                # Mark blocks which have a single ramp or more with a different texture
                breakOut = False
                for iix in xrange(4):
                    newx = ix*4+iix
                    for iiy in xrange(4):
                        newy = iy*4+iiy
                        if newx >= self.base.WC3map_xSize or newy >= self.base.WC3map_ySize:
                            break
                        if self.base.WC3map_rampmap.getVal(newx, newy) == 1:
                            block.set_material("brick/brick_ext_08")
                            breakOut = True
                            break
                    if breakOut:
                        break
                            
                
                Blockgroups.sew_brush_neighbours(ix, iy)
                blob = Blockgroups.getBlob(ix, iy)
                
                isFlat = True
                origValue = None
                
                distances_list = []
                for rowNumber in xrange(17):
                    row = blob.getRow(rowNumber)
                    row = row.tolist()
                    distances_list.append(row)
                    
                    if isFlat == True:
                        if origValue == None:
                            origValue = row[0]
                            
                        for val in row:
                            if val != origValue: 
                                isFlat = False
                                break
                        
                    #row = map(map_list_with_vertex, row)
                if isFlat:
                    height = origValue
                    vert = vmflib.types.Vertex((ix*4*wc3_tileSize)-vmf_xoffset+2*wc3_tileSize, 
                                               (iy*4*wc3_tileSize)-vmf_yoffset+2*wc3_tileSize, 
                                               (wc3_tileHeight//2)+(height//2))
                    block.origin = vert
                    
                    block.dimensions = (4*wc3_tileSize, 4*wc3_tileSize, wc3_tileHeight+height)
                    
                    block.update_sides()
                else:
                    block.top().set_dispInfo(4, normals_list, distances_list)
                
                self.base.m.world.children.append(block)