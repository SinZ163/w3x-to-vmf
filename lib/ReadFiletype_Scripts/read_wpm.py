#path map file
from lib.DataReader import DataReader

class ReadPathFile:
    def __init__(self, filename):
        self.read = DataReader(filename)
        self.info = {}
        self.__work__()
        
    def __work__(self):  
        self.info["fileID"] = self.read.charArray(4) #usually MP3W
        self.info["fileVersion"] = self.read.int() #usually 0
        self.info["pathWidth"] = self.read.int() #mapWidth * 4
        self.info["pathHeight"] = self.read.int() #mapHeight * 4
        self.info["info"] = []
        
        for x in xrange(0,self.info["pathWidth"]):
            xInfo = []
            
            for y in xrange(0,self.info["pathHeight"]):
                xInfo.append(self.read.byte())
                '''
                0x01: 0 (unused)
                0x02: 1=no walk, 0=walk ok
                0x04: 1=no fly, 0=fly ok
                0x08: 1=no build, 0=build ok
                0x10: 0 (unused)
                0x20: 1=blight, 0=normal
                0x40: 1=no water, 0=water
                0x80: 1=unknown, 0=normal
                 '''
            self.info["info"].append(xInfo)
            
#WE DID IT ALREADY!
if __name__ == "__main__":
    import os
    import simplejson
    filename = "input/war3map.wpm"
    pathInfo = ReadPathFile(filename)
    try:
        os.makedirs('./output')
    except OSError:
        pass
    with open("output/pathInfo.json", "w") as f:
        f.write(simplejson.dumps(pathInfo.info, sort_keys=True, indent=4 * ' '))