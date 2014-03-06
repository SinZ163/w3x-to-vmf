import lib.vmflib as vmflib
import lib.vmflib.tools as tools
from lib.dataTypes import Bytemap


class VmfGen():
    def __init__(self, base):
        # base is an instance of the War
        self.base = base
        self.name = "Brush VMF"
        self.description = "Brush-based VMF creation using a simple algorithm to reduce the amount of brushes used."
        
        print "{0} initialized".format(self.name)
    
    def create_vmf(self):
        wc3map_xSize = self.base.WC3map_xSize
        wc3map_ySize = self.base.WC3map_ySize
        
        wc3_tileSize = self.base.wc3_tileSize
        wc3_tileHeight = self.base.wc3_tileHeight
        blobAffinity = Bytemap(wc3map_xSize, wc3map_xSize)
        bloblist = []
        
        # We iterate a second time to group tiles of similar height together.
        # rectangularCheck uses a brute force approach.
        for x in xrange(wc3map_xSize):
            for y in xrange(wc3map_ySize):
                
                localHeight = self.base.WC3map_heightmap.getVal(x,y)
                
                # We check if the tile already belongs to a group.
                # -1 means no. If not equal to -1, we skip it.
                if blobAffinity.getVal(x, y) == -1:
                    endX, endY = self.rectangularCheck(x, y, localHeight, blobAffinity)
                    
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
            
            boxWidth = endX-startX
            boxLength = endY-startY
            
            height = (height)*wc3_tileHeight # Each layer of the map has a height of 64 units
            
            # midX and midY: middle of box that spans from startX;startY to endX;endY
            midX = startX + boxWidth/2.0 # Very important, DO NOT ROUND: causes issues with random overlapping
            midY = startY + boxLength/2.0
            
            # A little bit of optimization, only draw the block if it has a non-zero height
            # (Hammer only likes blocks with non-zero dimensions, for good reason)
            if height > 0:
                vert = vmflib.types.Vertex((midX*wc3_tileSize)-self.base.vmfmap_xMidOffset, 
                                           (midY*wc3_tileSize)-self.base.vmfmap_yMidOffset, 
                                           0+(height//2))
                block = tools.Block(origin = vert, dimensions=(boxWidth*wc3_tileSize, boxLength*wc3_tileSize, height))
                
                block.set_material("nature/dirt_grass_00")
                
                self.base.m.world.children.append(block)
    

        print "Building map finished."
    
    def rectangularCheck(self, startX, startY, neededHeight, blobAffinity):
        do_break = False
        
        x_limit = wc3map_xSize
        y_limit = wc3map_ySize
        
        for x in xrange(startX, x_limit):
            for y in xrange(startY, y_limit):
                # We check if the current value is what we need and if the current tile belongs
                # to a "blob", i.e. a rectangular block of tiles grouped together.
                if self.base.WC3map_heightmap.getVal(x, y) == neededHeight and blobAffinity.getVal(x, y) == -1:
                    pass
                
                else:
                    # We check at least two columns of tiles before deciding whether to break out of
                    # the loop completely.
                    if x > startX:
                        do_break = True
                    else:
                        y_limit = y
                    break
                
            if do_break == True:
                x_limit = x
                break
                    
        return (x_limit, y_limit)