#the info file

#Note, something is wrong atm, as readUpgradeData never gets called, as we run out of bytes =S (we run out reading how many upgradeData there is) I 

#Note 2) The format appears to be very complicated. Doublechecking the code against the wc3 specs 
#        and changing the code into something that is more friendly for debugging might be necessary
import struct

from lib.DataReader import DataReader

class WC3Info:
    def __init__(self, filename):
        self.read = DataReader(filename)
    
    def ReadFile(self):
        self.info = self.ReadInfo()
    
    def ReadInfo(self):
        info = {}
        
        info["version"] = self.read.int()
        info["saveCount"] = self.read.int()
        info["editVersion"] = self.read.int()
        info["name"] = self.read.string()
        info["author"] = self.read.string()
        info["description"] = self.read.string()
        info["recommendedPlayers"] = self.read.string()
        
        info["cameraBounds"] = [
                self.read.float(), #1
                self.read.float(), #2
                self.read.float(), #3
                self.read.float(), #4
                self.read.float(), #5
                self.read.float(), #6
                self.read.float(), #7
                self.read.float()  #8
            ]
        info["cameraComplements"] = [
                self.read.int(),
                self.read.int(),
                self.read.int(),
                self.read.int()
            ]
        
        info["playWidth"] = self.read.int()
        info["playHeight"] = self.read.int()
        info["flags"] = self.read.flags()
        info["groundType"] = self.read.char()
        info["backgroundImageID"] = self.read.int() #-1 == none or custom,
        info["customLoadingScreen"] = self.read.string() #empty if none or not custom,
        info["loadingText"] = self.read.string()
        info["loadingTitle"] = self.read.string()
        info["loadingSubtitle"] = self.read.string()
        info["gameDataSet"] = self.read.int() #index in the preset list, 0=standard,
        info["prologuePath"] = self.read.string()
        info["prologueText"] = self.read.string()
        info["prologueTitle"] = self.read.string()
        info["prologueSubtitle"] = self.read.string()
        
        
        info["useTerrainFog"] = self.read.int() #0 == not used, >0 = index of terrain fog style dropdown
        info["fogInfo"] = {
                "startZ" : self.read.float(),
                "endZ" : self.read.float(),
                "density" : self.read.float(),
                "red" : self.read.byte(),
                "green" : self.read.byte(),
                "blue" : self.read.byte(),
                "alpha" : self.read.byte()
            }
        
        info["weatherID"] = self.read.int() #0=none, else is the id in TerrainArt\Weather.slk
        info["soundEnvironment"] = self.read.string()
        info["tilesetLightID"] = self.read.char()
        info["waterInfo"] = {
                "red" : self.read.byte(),
                "green" : self.read.byte(),
                "blue" : self.read.byte(),
                "alpha" : self.read.byte()
            }
        
        info["playerData"] = self.ReadArray(self.readPlayerData)
        info["forceData"] = self.ReadArray(self.readForceData)
        info["upgradeData"] = self.ReadArray(self.readUpgradeData)
        info["techData"] = self.ReadArray(self.readTechData)
        info["unitData"] = self.ReadArray(self.readUnitData)
        info["itemData"] = self.ReadArray(self.readItemData)
    
    def ReadArray(self, func):
        print "Starting to read an array!"
        
        arrayInfo = {}
        arrayInfo["count"] = self.read.int()
        arrayInfo["data"] = []
        
        print "{0} elements in this array. Using {1} for reading.".format(arrayInfo["count"], func.__name__)
        
        for i in xrange(arrayInfo["count"]):
            data = func()
            arrayInfo["data"].append(data)
            
        return arrayInfo
    
    def readPlayerData(self):
        playerData = {}
        playerData["playerNumber"] = self.read.int()
        playerData["playerType"] = self.read.int()
        playerData["race"] = self.read.int()
        playerData["startPos"] = self.read.int()
        playerData["name"] = self.read.string()
        playerData["startX"] = self.read.float()
        playerData["startY"] = self.read.float()
        playerData["allyLowFlags"] = self.read.int()
        playerData["allyHighFlags"] = self.read.int()
        
        #print("###PLAYER DATA###")
        #print("PlayerType: "+str(playerData["playerType"]))
        #print("Race: "+str(playerData["race"]))
        #print("startPos "+str(playerData["startPos"]))
        
        return playerData
    
    def readForceData(self):
        forceData = {}
        forceData["flags"] = self.read.flags()
        forceData["mask"] = self.read.int()
        forceData["name"] = self.read.string()
        
        print(forceData)
        return forceData
    
    def readUpgradeData(self):
        upgradeData = {}
        upgradeData["flags"] = self.read.flags()
        upgradeData["id"] = self.read.charArray(4)
        upgradeData["level"] = self.read.int()
        upgradeData["Availability"] = self.read.int()
        
        return upgradeData
        
    def readTechData(self):
        techData = {}
        techData["flags"] = self.read.flags()
        techData["id"] = self.read.charArray(4)
        
        return techData
        
    def readUnitData(self):
        groupCount = self.read.int()
        
        for i in xrange(groupCount):
            groupInfo = {}
            groupInfo["number"] = self.read.int()
            groupInfo["name"] = self.read.string()
            groupInfo["posCount"] = self.read.int() #columns
            groupInfo["tableTypes"] = []
            groupInfo["entities"] = []
            
            for j in xrange(groupInfo["posCount"]):
                tableType = self.read.int()
                groupInfo["tableTypes"].append(tableType)
                
            groupInfo["unitCount"] = self.read.int() #rows
            
            for j in xrange(groupInfo["unitCount"]):
                entity = {}
                entity["chance"] = self.read.int()
                entity["ids"] = [self.read.charArray(4) for k in xrange(groupInfo["posCount"])]
                
                groupInfo["entities"].append(entity)
    
    def readItemData(self):
        itemInfo = {}
        itemInfo["tableCount"] = self.read.int()
        itemInfo["table"] = []
        
        for i in xrange(itemInfo["tableCount"]):
            tableInfo = {}
            
            tableInfo["tableNumber"] = self.read.int()
            tableInfo["tableName"] = self.read.string()
            tableInfo["setCount"] = self.read.int()
            tableInfo["set"] = []
            
            for j in xrange(tableInfo["setCount"]):
                setInfo = {}
                setInfo["itemCount"] = self.read.int()
                setInfo["items"] = []
                
                for k in xrange(setInfo["itemCount"]):
                    itemData = {}
                    itemData["percentualChance"] = self.read.int()
                    itemData["itemID"] = self.read.charArray(4)
                    
                    setInfo["item"].append(itemData)
                    
                tableInfo["set"].append(setInfo)
                
            itemInfo["table"].append(tableInfo)
            
        return itemInfo
        
if __name__ == "__main__":
    import os
    import simplejson
    #this is where shit happens!
    filename = "input/war3map.w3i"
    
    try:
        wc3Info = WC3Info(filename)
        wc3Info.ReadFile()
    finally:
        print "Reading index is at {0}. Maximum possible index: {1}".format(wc3Info.read.index, wc3Info.read.maxSize)
        
    
    try:
        os.makedirs('./output')
    except OSError:
        pass
    with open("output/info.json", "w") as f:
        f.write(simplejson.dumps(wc3Info.info, sort_keys=True, indent=4 * ' '))