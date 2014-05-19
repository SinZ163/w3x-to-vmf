from lib.DataReader import DataReader

class ReadDoodad:
    def __init__(self, filename):
        self.read = DataReader(filename)
        self.info = self.ReadDoodad()
        
    def ReadDoodad(self):
        doodHeader = self.ReadHeader()
        
        doodInfo = {}
        doodInfo["fileID"] = doodHeader[0]
        doodInfo["version"] = doodHeader[1]
        doodInfo["subversion"] = doodHeader[2]
        doodInfo["count"] = doodHeader[3]
        
        print "File ID: {0}, Version: {1}, Subversion: {2}".format(doodInfo["fileID"],
                                                                   doodInfo["version"],
                                                                   doodInfo["subversion"])
        print "Reading {0} trees".format(doodInfo["count"])
        
        doodInfo["trees"] = []
        
        for i in xrange(0, doodInfo["count"]):
            doodInfo["trees"].append(self.ReadTreeData())
            
        doodInfo["special"] = self.ReadSpecialDoodads()
        
        return doodInfo
        
    def ReadHeader(self):
        fileID = self.read.charArray(4)
        version = self.read.int()
        subversion = self.read.int()
        count = self.read.int()
        
        return fileID, version, subversion, count
        
    def ReadTreeData(self):
        treeInfo = {
            "treeID" : self.read.charArray(4),
            "variation" : self.read.int(),
            "coord" : {
                "x" : self.read.float(),
                "y" : self.read.float(),
                "z" : self.read.float()
            },
            "angle" : self.read.float(),
            "scale" : {
                "x" : self.read.float(),
                "y" : self.read.float(),
                "z" : self.read.float()
            },
            "flags" : self.read.byte(),
            "life" : self.read.byte()
        }
        
        treeInfo["itemPoint"] = self.read.int()
        treeInfo["numberOfItemSets"] = self.read.int()
        
        if treeInfo["numberOfItemSets"] > 0:
            treeInfo["itemSets"] = []
        
        ## Reading Item Set
        for i in xrange(treeInfo["numberOfItemSets"]):
            numberOfItems = self.read.int()
            itemSet = []
            
            ## Each Item Set has a Number of Items
            for j in xrange(numberOfItems):
                itemID = self.read.charArray(4)
                procentualChance = self.read.int()
                
                itemSet.append((itemID, procentualChance))
            
            treeInfo["itemSets"].append(itemSet)
                
        treeInfo["doodID"] = self.read.int()
        
        return treeInfo
        
    def ReadSpecialDoodads(self):
        specialInfo = {}
        specialInfo["version"] = self.read.int()
        specialInfo["count"] = self.read.int()
        specialInfo["info"] = []
        
        print "Reading special doodads. Version: {0}, Count: {1}".format(specialInfo["version"], specialInfo["count"])
        
        for i in xrange(specialInfo["count"]):
            ID = self.read.charArray(4)
            z, x, y = self.read.int(), self.read.int(), self.read.int()
            
            specialInfo["info"].append({"ID" : ID, 
                                        "x" : x,"y" : y, "z" : z})
            
        return specialInfo

if __name__ == "__main__":
    import os
    import sys
    import simplejson
    
    dooRead = ReadDoodad(sys.argv[1])
    
    try:
        os.makedirs('./output')
    except OSError:
        pass
    with open("output/treeInfo.json", "w") as f:
        f.write(simplejson.dumps(dooRead.info, sort_keys=True, indent=4 * ' '))
        
    #Ok, lets just do an x,y dump of every tree (WTst id only)
    #treeDB = []
    #for tree in dooRead.info["trees"]:
    #    if tree["treeID"] == "WTst":
    #        treeDB.append({"x" : tree["coord"]["x"], "y" : tree["coord"]["y"]})
    #with open("output/treeDump.json", "w") as f:
    #    f.write(simplejson.dumps(treeDB, sort_keys=True, indent=4 * ' '))