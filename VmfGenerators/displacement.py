

class VmfGen():
    def __init__(self, base):
        self.base = base
        self.name = "Displacement VMF"
        self.description = "Displacement-based VMF creation using fixed-size brushes and displacements."
        
        print "{0} initialized".format(self.name)
    
    def create_vmf(self):
        Blockgroups = QuadBlobs(xSize//4, ySize//4, 4, 4)
        
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
                            
                            # Is the ramp flag set? If so, we will try to draw a transition between two layers
                            if rampMap.getVal(newX, newY) == 1 and False: # for the moment disabled because of issues
                                upperTile = heightmap.getVal(newX, newY+1)
                                lowerTile = heightmap.getVal(newX, newY-1)
                                leftTile = heightmap.getVal(newX-1, newY)
                                rightTile = heightmap.getVal(newX+1, newY)
                                
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
                                        blob.setVal(iix*4+local_x+xoffset, iiy*4+local_y+yoffset, average*64)
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
                                
                                blob.setVal(local_x, local_y, currentHeight*64)
            
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
            
            # Mark blocks which have a single ramp or more with a different texture
            breakOut = False
            for iix in xrange(4):
                newx = ix*4+iix
                for iiy in xrange(4):
                    newy = iy*4+iiy
                    if newx >= data.mapInfo["width"] or newy >= data.mapInfo["height"]:
                        break
                    if rampMap.getVal(newx, newy) == 1:
                        block.set_material("brick/brick_ext_08")
                        breakOut = True
                        break
                if breakOut:
                    break
                        
            
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