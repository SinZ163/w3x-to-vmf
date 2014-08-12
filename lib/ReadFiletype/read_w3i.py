
# Reading the war3map.w3i file. The file contains various useful information 
# related to the map, e.g. description, number of recommended players, and more.
# 
# Note:  Sometimes w3i files appear to be incomplete. Is this because the file was
#        extracted incorrectly from the map, or is WC3 tolerant to incomplete data?
#        More specifically, the arrays at the end of the w3i file appear to be missing,
#        possibly because the data is not needed and can be filled in by WC3?


import struct
import traceback

from lib.DataReader import DataReader

#class WC3Info:
#    def __init__(self, filename):
#        self.read = DataReader(filename)
def read_W3I(filehandle, triggerStrings = None):    
#    def ReadFile(self):
#        self.info = {}
#        self.ReadInfo()
    read = DataReader(filehandle)
    if triggerStrings != None:
        read.load_triggerDB(triggerStrings)
        
    info = {}
    
    info["version"] = read.int()
    #print info["version"]
    
    info["saveCount"] = read.int()
    info["editVersion"] = read.int()
    info["name"] = read.string()
    info["author"] = read.string()
    info["description"] = read.string()
    info["recommendedPlayers"] = read.string()
    
    info["cameraBounds"] = [
            read.float(), #1
            read.float(), #2
            read.float(), #3
            read.float(), #4
            read.float(), #5
            read.float(), #6
            read.float(), #7
            read.float()  #8
        ]
    info["cameraComplements"] = [
            read.int(),
            read.int(),
            read.int(),
            read.int()
        ]
    
    info["playWidth"] = read.int()
    info["playHeight"] = read.int()
    info["flags"] = read.flags()
    info["groundType"] = read.char()
    info["backgroundImageID"] = read.int() #-1 == none or custom,
    info["customLoadingScreen"] = read.string() #empty if none or not custom,
    info["loadingText"] = read.string()
    info["loadingTitle"] = read.string()
    info["loadingSubtitle"] = read.string()
    info["gameDataSet"] = read.int() #index in the preset list, 0=standard,
    info["prologuePath"] = read.string()
    info["prologueText"] = read.string()
    info["prologueTitle"] = read.string()
    info["prologueSubtitle"] = read.string()
    
    
    info["useTerrainFog"] = read.int() #0 == not used, >0 = index of terrain fog style dropdown
    info["fogInfo"] = {
            "startZ" : read.float(),
            "endZ" : read.float(),
            "density" : read.float(),
            "red" : read.byte(),
            "green" : read.byte(),
            "blue" : read.byte(),
            "alpha" : read.byte()
        }
    
    info["weatherID"] = read.int() #0=none; else = the id is in TerrainArt\Weather.slk
    info["soundEnvironment"] = read.string()
    info["tilesetLightID"] = read.char()
    info["waterInfo"] = {
            "red" : read.byte(),
            "green" : read.byte(),
            "blue" : read.byte(),
            "alpha" : read.byte()
        }
    
    info["playerData"] = __ReadArray__(read, __readPlayerData__ )
    
    try:
        info["forceData"] = __ReadArray__(read, __readForceData__ )
    except struct.error:
        info["forceData"] = None
    
    try:
        info["upgradeData"] = __ReadArray__(read, __readUpgradeData__ )
    except struct.error:
        info["upgradeData"] = None
        
    try:
        info["techData"] = __ReadArray__(read, __readTechData__ )
    except struct.error:
        info["techData"] = None
        
    try:
        info["unitData"] = __ReadArray__(read, __readUnitData__ )
    except struct.error:
        info["unitData"] = None
        
    #print info["playerData"]
    #print info["forceData"]
    #print info["upgradeData"]
    #print info["techData"]
    #print info["unitData"]
    
    try:
        info["itemData"] = __ReadArray__(read, __readItemData__ )
    except struct.error:
        info["itemData"] = None
    
    return info




    
def __ReadArray__(read, readArrayData_function):
    #print "Starting to read an array!"
    
    arrayInfo = {}
    arrayInfo["data"] = []
    
    try:
        arrayInfo["count"] = read.int()
    
    except struct.error:
        arrayInfo["count"] = 0
        #print "Array does not exist. Function: {0}".format(readArrayData_functiona.__name__)
        
        return arrayInfo
    
    else:
        #print "{0} elements in this array. Using {1} for reading.".format(arrayInfo["count"], readArrayData_function.__name__)
        
        for i in xrange(arrayInfo["count"]):
            data = readArrayData_function(read)
            arrayInfo["data"].append(data)
            
        return arrayInfo

def __readPlayerData__(read):
    playerData = {}
    playerData["playerNumber"] = read.int()
    playerData["playerType"] = read.int()
    playerData["race"] = read.int()
    playerData["startPos"] = read.int()
    playerData["name"] = read.string()
    playerData["startX"] = read.float()
    playerData["startY"] = read.float()
    playerData["allyLowFlags"] = read.int()
    playerData["allyHighFlags"] = read.int()
    
    #print("###PLAYER DATA###")
    #print("PlayerType: "+str(playerData["playerType"]))
    #print("Race: "+str(playerData["race"]))
    #print("startPos "+str(playerData["startPos"]))
    
    return playerData

def __readForceData__(read):
    forceData = {}
    forceData["flags"] = read.flags()
    forceData["mask"] = read.int()
    forceData["name"] = read.string()
    
    #print(forceData)
    return forceData

def __readUpgradeData__(read):
    upgradeData = {}
    upgradeData["flags"] = read.flags()
    upgradeData["id"] = read.charArray(4)
    upgradeData["level"] = read.int()
    upgradeData["Availability"] = read.int()
    
    return upgradeData
    
def __readTechData__(read):
    techData = {}
    techData["flags"] = read.flags()
    techData["id"] = read.charArray(4)
    
    return techData
    
def __readUnitData__(read):
    groupCount = read.int()
    
    for i in xrange(groupCount):
        groupInfo = {}
        groupInfo["number"] = read.int()
        groupInfo["name"] = read.string()
        groupInfo["posCount"] = read.int() #columns
        groupInfo["tableTypes"] = []
        groupInfo["entities"] = []
        
        for j in xrange(groupInfo["posCount"]):
            tableType = read.int()
            groupInfo["tableTypes"].append(tableType)
            
        groupInfo["unitCount"] = read.int() #rows
        
        for j in xrange(groupInfo["unitCount"]):
            entity = {}
            entity["chance"] = read.int()
            entity["ids"] = [read.charArray(4) for k in xrange(groupInfo["posCount"])]
            
            groupInfo["entities"].append(entity)
    
    return groupInfo

def __readItemData__(read):
    itemInfo = {}
    itemInfo["tableCount"] = read.int()
    itemInfo["table"] = []
    
    for i in xrange(itemInfo["tableCount"]):
        tableInfo = {}
        
        tableInfo["tableNumber"] = read.int()
        tableInfo["tableName"] = read.string()
        tableInfo["setCount"] = read.int()
        tableInfo["set"] = []
        
        for j in xrange(tableInfo["setCount"]):
            setInfo = {}
            setInfo["itemCount"] = read.int()
            setInfo["items"] = []
            
            for k in xrange(setInfo["itemCount"]):
                itemData = {}
                itemData["percentualChance"] = read.int()
                itemData["itemID"] = read.charArray(4)
                
                setInfo["items"].append(itemData)
                
            tableInfo["set"].append(setInfo)
            
        itemInfo["table"].append(tableInfo)
        
    return itemInfo

"""
if __name__ == "__main__":
    import os
    import simplejson
    import sys
    #this is where shit happens!
    filename = sys.argv[1]
    
    try:
        wc3Info = WC3Info(filename)
        wc3Info.ReadFile()
    except struct.error:
        print "Encountered struct error. Traceback:"
        print traceback.format_exc()
        print "Ignoring error. Please note that the data might be not entirely correct."
    finally:
        print "Reading index is at {0}. Maximum possible index: {1}.".format(wc3Info.read.index, wc3Info.read.maxSize)
        if wc3Info.read.index > wc3Info.read.maxSize:
            print "Conclusion: Tried to read more data than exists in the file." 
        
    
    try:
        os.makedirs('./output')
    except OSError:
        pass
    
    print
    print "Saving data to output/info.json..."
    
    with open("output/info.json", "w") as f:
        f.write(simplejson.dumps(wc3Info.info, sort_keys=True, indent=4 * ' '))
    
    print "Done!" """