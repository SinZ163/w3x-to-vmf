from lib.DataReader import DataReader


def read_doodad(filehandle):
    read = DataReader(filehandle)
    doodHeader = __read_header__(read)
    
    doodInfo = {}
    doodInfo["fileID"] = doodHeader[0]
    doodInfo["version"] = doodHeader[1]
    doodInfo["subversion"] = doodHeader[2]
    doodInfo["count"] = doodHeader[3]
    
    #print "File ID: {0}, Version: {1}, Subversion: {2}".format(doodInfo["fileID"],
    #                                                           doodInfo["version"],
    #                                                           doodInfo["subversion"])
    #print "Reading {0} trees".format(doodInfo["count"])
    
    doodInfo["trees"] = []
    
    for i in xrange(0, doodInfo["count"]):
        doodInfo["trees"].append(__read_treedata__(read))
        
    doodInfo["special"] = __read_specialdoodads__(read)
    
    return doodInfo
    
def __read_header__(read):
    fileID = read.charArray(4)
    version = read.int()
    subversion = read.int()
    count = read.int()
    
    return fileID, version, subversion, count
    
def __read_treedata__(read):
    treeInfo = {
        "treeID" : read.charArray(4),
        "variation" : read.int(),
        "coord" : {
                   "x" : read.float(),
                   "y" : read.float(),
                   "z" : read.float()
        },
        "angle" : read.float(),
        "scale" : {
                   "x" : read.float(),
                   "y" : read.float(),
                   "z" : read.float()
        },
        "flags" : read.byte(),
        "life" : read.byte()
    }
    
    treeInfo["itemPoint"] = read.int()
    treeInfo["numberOfItemSets"] = read.int()
    
    if treeInfo["numberOfItemSets"] > 0:
        treeInfo["itemSets"] = []
    
    ## Reading Item Set
    for i in xrange(treeInfo["numberOfItemSets"]):
        numberOfItems = read.int()
        itemSet = []
        
        ## Each Item Set has a Number of Items
        for j in xrange(numberOfItems):
            itemID = read.charArray(4)
            procentualChance = read.int()
            
            itemSet.append( (itemID, procentualChance) )
        
        treeInfo["itemSets"].append(itemSet)
            
    treeInfo["doodID"] = read.int()
    
    return treeInfo
    
def __read_specialdoodads__(read):
    specialInfo = {}
    specialInfo["version"] = read.int()
    specialInfo["count"] = read.int()
    specialInfo["info"] = []
    
    #print "Reading special doodads. Version: {0}, Count: {1}".format(specialInfo["version"], specialInfo["count"])
    
    for i in xrange(specialInfo["count"]):
        ID = read.charArray(4)
        z, x, y = read.int(), read.int(), read.int()
        
        specialInfo["info"].append({"ID" : ID, 
                                    "x" : x,"y" : y, "z" : z})
        
    return specialInfo


"""
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
        f.write(simplejson.dumps(dooRead.info, sort_keys=True, indent=4 * ' '))"""
        
    #Ok, lets just do an x,y dump of every tree (WTst id only)
    #treeDB = []
    #for tree in dooRead.info["trees"]:
    #    if tree["treeID"] == "WTst":
    #        treeDB.append({"x" : tree["coord"]["x"], "y" : tree["coord"]["y"]})
    #with open("output/treeDump.json", "w") as f:
    #    f.write(simplejson.dumps(treeDB, sort_keys=True, indent=4 * ' '))