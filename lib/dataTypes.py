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
        
        blob = Bytemap(self.blobSizeX**2+1, self.blobSizeY**2+1)
        
        self.blobmap[index] = blob
    
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
        x, y = maxCoords[0] - minCoords[0], maxCoords[1] - minCoords[1]
        
        subBlobList = self.getValGroup(minCoords, maxCoords, True)
        
        return Bytemap(x, y, 0, subBlobList)
    
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