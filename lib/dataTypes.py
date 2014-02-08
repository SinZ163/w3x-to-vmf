import array

class QuadBlobs():
    def __init__(self, maxX, maxY, blobSizeX, blobSizeY):
        self.maxX = maxX
        self.maxY = maxY
        
        self.blobSizeX = blobSizeX
        self.blobSizeY = blobSizeY
        
        self.blobmap = [False for i in xrange(maxX*maxY)]
    
    def addBlob(self, x, y):
        index = y * self.maxX + x
        
        blob = Bytemap(self.blobSizeX**2+1, self.blobSizeY**2+1, dataType = "f")
        
        self.blobmap[index] = blob
        
        return blob
    
    def getBlob(self, x, y):
        index = y * self.maxX + x
        
        return self.blobmap[index]
    
    def getTile(self, blobX, blobY, tileX, tileY):
        # Displacement maps are not even, so we will calculate an offset
        # to keep the tiles close to the edges of the blob.
        # Check the sewTilesTogether function on what happens to the
        # data in between the tiles. 
        if tileX > 1: x_offset = 1
        else: x_offset = 0
        
        if tileY > 1: y_offset = 1
        else: y_offset = 0
        
        tileX = tileX * self.blobSizeX
        tileY = tileY * self.blobSizeY
        
        tiledata = self.getBlob(blobX, blobY).getSubBlob((tileX+x_offset,                   tileY+y_offset), 
                                                         (tileX+x_offset+self.blobSizeX,    tileY+y_offset+self.blobSizeY))
        
        return tiledata
    
    def changeTile(self, blobX, blobY, tileX, tileY, tile):
        if tileX > 1: x_offset = 1
        else: x_offset = 0
        
        if tileY > 1: y_offset = 1
        else: y_offset = 0
        
        blob = self.getBlob(blobX, blobY)
        
        tileX = tileX * self.blobSizeX
        tileY = tileY * self.blobSizeY
        
        blob.setValGroup_fromBlob(tile, 
                                  (tileX+x_offset,                tileY+y_offset), 
                                  (tileX+x_offset+self.blobSizeX, tileY+y_offset+self.blobSizeY))
    
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
        
    
    def sew_brush_neighbours(self, blobx, bloby):
        # x;y coordinates of the corners of a blob
        corners = [(0,0), (0, 16), (16, 0), (16, 16)]
        
        # We create a list of the coordinates of the sides
        # for simple iteration.
        sideUp = [(x, 16) for x in xrange(1, 16)]
        sideDown = [(x, 0) for x in xrange(1, 16)]
        sideLeft =  [(0, y) for y in xrange(1, 16)]
        sideRight = [(16, y) for y in xrange(1, 16)]
        
        currBlob = self.getBlob(blobx, bloby)
        
        
        if bloby+1 < self.maxY: # Boundary check
            
            upperBlob = self.getBlob(blobx, bloby+1)
            
            # We are iterating over two lists at once so we can grab the coordinates
            # of two neighbouring displacement points.
            for coords, coordsUpper in zip(sideUp, sideDown):
                ix, iy = coords
                ix_up, iy_up = coordsUpper
                
                currHeight = currBlob.getVal(ix, iy)
                otherHeight = upperBlob.getVal(ix_up, iy_up)
                
                average = (currHeight+otherHeight)/2.0

                currBlob.setVal(ix, iy, average)
                upperBlob.setVal(ix_up, iy_up, average)
                
                
        if blobx+1 < self.maxX: # Boundary check
            
            rightBlob = self.getBlob(blobx+1, bloby)
            
            for coords, coordsRight in zip(sideRight, sideLeft): 
                ix, iy = coords
                ix_right, iy_right = coordsRight
                
                currHeight = currBlob.getVal(ix, iy)
                otherHeight = rightBlob.getVal(ix_right, iy_right)
                
                average = (currHeight+otherHeight)/2.0
                
                currBlob.setVal(ix, iy, average)
                rightBlob.setVal(ix_right, iy_right, average)
        """if bloby-1 >= 0:
            lowerBlob = self.getBlob(blobx, bloby-1)
            for coords, coordsLower in zip(sideDown, sideUp):
                ix, iy = coords
                ix_down, iy_down = coordsLower
                
                currHeight = currBlob.getVal(ix, iy)
                otherHeight = lowerBlob.getVal(ix_down, iy_down)
                
                diff = abs(currHeight-otherHeight)/2.0
                average = (currHeight+otherHeight)/2.0
                
                diff = currHeight < otherHeight and diff or -diff-64
                if currHeight == otherHeight: diff = 0
                
                currBlob.setVal(ix, iy, currHeight+diff)"""
        
        """if blobx-1 >= 0:
            leftBlob = self.getBlob(blobx-1, bloby)
            for coords, coordsLeft in zip(sideLeft, sideRight):
                ix, iy = coords
                ix_left, iy_left = coordsLeft
                
                currHeight = currBlob.getVal(ix, iy)
                otherHeight = leftBlob.getVal(ix_left, iy_left)
                
                diff = abs(currHeight-otherHeight)/2.0
                average = (currHeight+otherHeight)/2.0
                
                diff = currHeight < otherHeight and diff or -diff-64
                if currHeight == otherHeight: diff = 0
                
                currBlob.setVal(ix, iy, currHeight+diff)"""
        
        
        
            
        
            
            
        
        
    
            
class Bytemap():
    def __init__(self, maxX, maxY, init = -1, initArray = None, dataType = "h"):
        self.maxX = maxX
        self.maxY = maxY
        
        if initArray == None:
            self.map = array.array(dataType, [init for x in xrange(maxX*maxY)])
        else:
            self.map = array.array(dataType, initArray)
            
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
                    
            
        
        for ix in xrange(minCoords[0],maxCoords[0]):
            for iy in xrange(minCoords[1],maxCoords[1]):
                yield ix, iy, self.getVal(ix, iy)
                
    def getValGroup(self, minCoords = (0,0), maxCoords = "max", noCoordinates = False):
        if maxCoords == "max":
            maxCoords = (self.maxX, self.maxY) 
        
        xsize, ysize = maxCoords[0] - minCoords[0], maxCoords[1] - minCoords[1]
        
        grouplist = [0 for i in xrange(xsize*ysize)]
        for ix in xrange(minCoords[0],maxCoords[0]):
            for iy in xrange(minCoords[1],maxCoords[1]):
                localx, localy = ix - minCoords[0], iy - minCoords[1]
                index = localy * xsize + localx
                if noCoordinates:
                    grouplist[index] = self.getVal(ix, iy)
                else:
                    grouplist[index] = (ix, iy, self.getVal(ix, iy))
        
        return grouplist
             
    def setValGroup_fromBlob(self, blob, minCoords, maxCoords):
        for ix in xrange(minCoords[0],maxCoords[0]):
            for iy in xrange(minCoords[1],maxCoords[1]):
                
                miniX, miniY = ix - minCoords[0], iy - minCoords[1]
                self.setVal(ix, iy, blob.getVal(miniX, miniY))
             
    
    def getSubBlob(self, minCoords, maxCoords):
        xsize, ysize = maxCoords[0] - minCoords[0], maxCoords[1] - minCoords[1]
        
        subBlobList = self.getValGroup(minCoords, maxCoords, True)
        
        return Bytemap(xsize, ysize, 0, subBlobList)
    
    # The data is ordered in such a way so that we can retrieve 
    # an entire row of data simply by calculating the start and end index.
    def getRow(self, rowNum):
        start = rowNum * self.maxX
        end = rowNum * self.maxX + self.maxX
        
        return self.map[start:end]
    
    # Columns are less simple to retrieve, we need to use the getVal method
    # which handles calculation of indexes. 
    # List comprehensions are fun, so we will use one.
    def getColumn(self, columnNum):
        x = columnNum
        #print self.maxX
        column = [self.getVal(x, y) for y in xrange(self.maxY)]
        
        return column
            
        

class TileMap(Bytemap):
    def __init__(self, *args):
        Bytemap.__init__(*args)