import struct
import time
import os
import traceback
#Yoshi, care to help with this
class DataReader():
    def __init__(self, filename):
        self.maxSize = os.path.getsize(filename) 
        self.hdlr = open(filename, "rb")
        self.index = 0
        
    def int(self):
        #Integer is 4 bytes, little endian
        self.index += 4
        data = self.hdlr.read(4)
        return struct.unpack("<i", data)[0]
    def short(self):
        #Short is 2 bytes, little endian
        self.index += 2
        data = self.hdlr.read(2)
        return struct.unpack("<h", data)[0]
    
    def float(self):
        #Float is 4 byte little endian
        self.index += 4
        data = self.hdlr.read(4)
        return struct.unpack("<f", data)[0]
    
    def char(self):
        #1 char = 1 byte
        self.index += 1
        data = self.hdlr.read(1)
        info = struct.unpack("c", data)[0]
        return info
    
    def charArray(self, len):
        info = []
        for i in range(0,len):
            info.append(self.char())
        return info
    
    def byte(self):
        #Not in the specifications, but is a byte..
        self.index += 1
        data = self.hdlr.read(1)
        return struct.unpack("B", data)[0]

"""
def readNibble():
    #Not in the specifications, but is a 4bit entry
    pass
    
def readString(): #not used in w3e, ignoring
    #is UTF-8
    #Read until \0 (null character)
    #If prefixed with "TRIGSTR_", it is to reference a string from memory
    pass
    
def readFlag(): #not used in w3e, ignoring
    #Flags are booleans stored in 4 bytes
    pass
"""
#f = open("war3map  .w3e", "rb")

read = DataReader("war3map.w3e")
try:
    
    data = {}
    data["fileID"] = read.charArray(4)
    data["formatVersion"] = read.int()
    data["mainTileSet"] = read.char()
    print("Primary Tileset: " + str(data["mainTileSet"]))
    data["customTileSet"] = read.int() #actually is a boolean
    print("Custom Tilesets: " + str(data["customTileSet"]))
    data["groundTileSetCount"] = read.int() #Shouldn't be greater than 16
    print(data["groundTileSetCount"])
    data["groundTilesets"] = []
    
    text = ""
    for i in range(0,data["groundTileSetCount"]):
        info = read.charArray(4)
        data["groundTilesets"].append(info)
        text = text + "{" + "".join(info)+"},"
        
    print(text)
    text = ""
    data["cliffTileSetCount"] = read.int() #Shouldn't be greater than 16
    print(data["cliffTileSetCount"])
    data["cliffTileSets"] = []
    for i in range(0,data["cliffTileSetCount"]):
        info = read.charArray(4)
        data["cliffTileSets"].append(info)
        text = text + "{" + "".join(info)+"},"
    print(text)
    
    data["width"] = read.int() # +1 = Mx
    data["height"] = read.int()# +1 = My
    
    data["maxWidth"] = data["width"] + 1
    data["maxHeight"] = data["height"] + 1
    
    data["offsetX"] = read.float()
    data["offsetY"] = read.float()
    
    #more data crap
    data["info"] = []
              #+1 is because this is getting info on corners
    i = 0
    print("Width: "+str(data["width"]))
    print("Height: "+str(data["height"]))
    time.sleep(10)
    
    
    #while i < (data["width"]+1)*(data["height"]+1):
    for i in xrange((data["width"])*(data["height"])):
        #print(i)
        tmpData = {}
        tmpData["groundHeight"] = read.short()
        tmpData["waterLevel"] = read.short() #bit 15 is used for boundary flag 1
        tmpData["nibble1"] = read.byte()
        #info[i]["flags"] = readNibble()
        #    #0x4000 = boundary flag 1
        #    #0x0010 = ramp flag
        #    #0x0020 = blight flag
        #    #0x0040 = water flag
        #    #0x0080 = boundary flag 2
        #info[i]["groundTextureType"] = readNibble()
        #    #will be a number between 1 and 16
        #    #i.e grass, dirt, rocks...
        tmpData["textureDetails"] = read.byte()
        tmpData["nibble2"] = read.byte()
        #info[i]["cliffTextureType"] = readNibble()
        #info[i]["layerHeight"] = readNibble()
        data["info"].append(tmpData)
        #i = i + 1
    #print(data)
except Exception as error:
    print traceback.format_exc()
    print error
    print read.index
    print read.maxSize
    print (data["width"]+1)*(data["height"]+1)
    print (data["width"])*(data["height"])
    