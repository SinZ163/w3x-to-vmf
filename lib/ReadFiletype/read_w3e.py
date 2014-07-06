from lib.DataReader import DataReader

def read_W3E(filehandle):
    read = DataReader(filehandle)
    mapinfo = __read_map__(read)
    
    return mapinfo


        
def __read_map__(read):
    mapInfo = __read_header__(read)
    mapInfo["info"] = []
    
    for i in xrange( mapInfo["width"]*mapInfo["height"] ):
        mapInfo["info"].append(__read_tile__(read))
        
    return mapInfo

def __read_header__(read):
    data = {}
    data["fileID"] = read.charArray(4)
    data["formatVersion"] = read.int()
    
    data["mainTileSet"] = read.char()        
    
     # This is a boolean, 1 means a custom tileset is used,
     # 0 means no custom tileset is used.
    data["customTileSetIsUsed"] = read.int()
    
    data["groundTileSets"] = __read_tileset__(read)
    data["cliffTileSets"] = __read_tileset__(read)
    
    data["width"] = read.int()
    data["height"] = read.int()
    
    data["offsetX"] = read.float()
    data["offsetY"] = read.float()
    
    return data

def __read_tileset__(read):
    length = read.int()
    info = [] 
    
    for i in range( length ):
        info.append(read.charArray(4))
        
    return info

def __read_tile__(read):
    tmpData = {}
    tmpData["groundHeight"] = read.short()
    tmpData["waterLevel"] = read.short() #bit 15 is used for boundary flag 1
    #tmpData["nibble1"] = self.read.byte()
    tmpData["flags"], tmpData["groundTextureType"] = read.nibbles()
    tmpData["textureDetails"] = read.byte()
    #tmpData["nibble2"] = self.read.byte() 
    tmpData["cliffTextureType"], tmpData["layerHeight"] = read.nibbles()
    
    return tmpData

"""
if __name__ == "__main__":
    import os
    import simplejson
    import sys
    
    filename = sys.argv[1]
    
    with open(filename, "rb") as mapfile:
        mapInfo = ReadW3E(mapfile)
        
        try:
            os.makedirs('./output')
        except OSError:
            pass
        with open("output/mapInfo.json", "w") as f:
            f.write(simplejson.dumps(mapInfo, sort_keys=True, indent=4 * ' '))"""