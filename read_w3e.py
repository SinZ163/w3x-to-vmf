class ReadW3E():
    from lib.DataReader import DataReader
    
    def __init__(self, filename):
        self.read = self.DataReader(filename)
        self.mapInfo = self.ReadMap()
        
    def ReadMap(self):
        mapInfo = self.ReadHeader()
        mapInfo["info"] = []
        for i in xrange((mapInfo["width"])*(mapInfo["height"])):
            mapInfo["info"].append(self.ReadTile())
        return mapInfo
    def ReadHeader(self):
        data = {}
        data["fileID"] = self.read.charArray(4)
        data["formatVersion"] = self.read.int()
        
        data["mainTileSet"] = self.read.char()        
        data["customTileSet"] = self.read.int() #actually is a boolean
        
        data["groundTileSets"] = self.ReadTileset()
        data["cliffTileSets"] = self.ReadTileset()
        
        data["width"] = self.read.int()
        data["height"] = self.read.int()
        
        data["offsetX"] = self.read.float()
        data["offsetY"] = self.read.float()
        return data
    
    def ReadTileset(self):
        length = self.read.int()
        info = [] 
        for i in range(0,length):
            info.append(self.read.charArray(4))
        return info
    
    def ReadTile(self):
        tmpData = {}
        tmpData["groundHeight"] = self.read.short()
        tmpData["waterLevel"] = self.read.short() #bit 15 is used for boundary flag 1
        #tmpData["nibble1"] = self.read.byte()
        tmpData["flags"], tmpData["groundTextureType"] = self.read.nibbles()
        tmpData["textureDetails"] = self.read.byte()
        #tmpData["nibble2"] = self.read.byte() 
        tmpData["cliffTextureType"], tmpData["layerHeight"] = self.read.nibbles()
        
        return tmpData

if __name__ == "__main__":
    import os
    import simplejson
    import sys
    
    filename = sys.argv[1]
    mapInfo = ReadW3E(filename)
    
    try:
        os.makedirs('./output')
    except OSError:
        pass
    with open("output/mapInfo.json", "w") as f:
        f.write(simplejson.dumps(mapInfo.mapInfo, sort_keys=True, indent=4 * ' '))