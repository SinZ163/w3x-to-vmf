#the info file

#Note, something is wrong atm, as readUpgradeData never gets called, as we run out of bytes =S (we run out reading how many upgradeData there is) I 

#Note 2) The format appears to be very complicated. Doublechecking the code against the wc3 specs 
#        and changing the code into something that is more friendly for debugging might be necessary

from lib.DataReader import DataReader

class WC3Info:
    def __init__(self, filename):
        self.read = DataReader(filename)
        
        self.info = self.ReadInfo()
        
    def ReadArray(self, func):
        print("Starting to read an array!")
        
        arrayInfo = {
            "count" : self.read.int(),
            "data" : []
        }
        
        print(str(arrayInfo["count"])+" elements in this array.")
        
        for i in xrange(0, arrayInfo["count"]):
            data = func()
            arrayInfo["data"].append(data)
            
        return arrayInfo
    
    def ReadInfo(self):
        return {
            "version"  : self.read.int(),
            "saveCount" : self.read.int(),
            "editVersion" : self.read.int(),
            "name"  : self.read.string(),
            "author" : self.read.string(),
            "description" : self.read.string(),
            "recPlayers" : self.read.string(),
            "cameraBounds" : [
                self.read.float(), #1
                self.read.float(), #2
                self.read.float(), #3
                self.read.float(), #4
                self.read.float(), #5
                self.read.float(), #6
                self.read.float(), #7
                self.read.float()  #8
            ],
            "cameraComplements" : [
                self.read.int(),
                self.read.int(),
                self.read.int(),
                self.read.int()
            ],
            "playWidth" : self.read.int(),
            "playHeight" : self.read.int(),
            "flags" : self.read.flags(),
            "groundType"  : self.read.char(),
            "backgroundImageID" : self.read.int(), #-1 == none or custom,
            "customLoadingScreen" : self.read.string(), #empty if none or not custom,
            "loadingText" : self.read.string(),
            "loadingTitle" : self.read.string(),
            "loadingSubtitle" : self.read.string(),
            "gameDataSet" : self.read.int(), #index in the preset list, 0=standard,
            "prologuePath" : self.read.string(),
            "prologueText" : self.read.string(),
            "prologueTitle" : self.read.string(),
            "prologueSubtitle" : self.read.string(),
            "useTerrainFog" : self.read.int(), #0 == not used, >0 = index of terrain fog style dropdown
            "fogInfo" : {
                "startZ" : self.read.float(),
                "endZ" : self.read.float(),
                "density" : self.read.float(),
                "red" : self.read.byte(),
                "green" : self.read.byte(),
                "blue" : self.read.byte(),
                "alpha" : self.read.byte()
            },
            "weatherID" : self.read.int(), #0=none, else is the id in TerrainArt\Weather.slk
            "soundEnvironment" : self.read.string(),
            "tilesetLightID" : self.read.char(),
            "waterInfo" : {
                "red" : self.read.byte(),
                "green" : self.read.byte(),
                "blue" : self.read.byte(),
                "alpha" : self.read.byte()
            },
            "playerData" : self.ReadArray(self.readPlayerData),
            "forceData" : self.ReadArray(self.readForceData),
            "upgradeData" : self.ReadArray(self.readUpgradeData),
            "techData" : self.ReadArray(self.readTechData),
            "unitData" : self.ReadArray(self.readUnitData),
            "itemData" : self.ReadArray(self.readItemData)
        }
        
    def readPlayerData(self):
        playerData = {
            "playerNumber" : self.read.int(),
            "playerType" : self.read.int(),
            "race" : self.read.int(),
            "startPos" : self.read.int(),
            "name" : self.read.string(),
            "startX" : self.read.float(),
            "startY" : self.read.float(),
            "allyLowFlags" : self.read.int(),
            "allyHighFlagS" : self.read.int()
        }
        #print("###PLAYER DATA###")
        #print("PlayerType: "+str(playerData["playerType"]))
        #print("Race: "+str(playerData["race"]))
        #print("startPos "+str(playerData["startPos"]))
        
        return playerData
    
    def readForceData(self):
        forceData = {
            "flags" : self.read.flags(),
            "mask" : self.read.int(),
            "name" : self.read.string()
        }
        #print(forceData)
        return forceData
    
    def readUpgradeData(self):
        return {
            "flags" : self.read.flags(),
            "id" : self.read.charArray(4),
            "level" : self.read.int(),
            "Availability" : self.read.int()
        }
        
    def readTechData(self):
        return {
            "flags" : self.read.flags(),
            "id" : slf.read.charArray(4)
        }
        
    def readUnitData(self):
        groupCount = self.read.int()
        for i in xrange(0,groupCount):
            groupInfo = {
                "number" : self.read.int(),
                "name" : self.read.string(),
                "posCount" : self.read.int(), #columns
                "tableTypes" : [],
                "entities" : []
            }
            for j in xrange(0,groupInfo["posCount"]):
                groupInfo["tableTypes"].append(self.read.int())
            groupInfo["unitCount"] = self.read.int() #rows
            for j in xrange(0, groupInfo["unitCount"]):
                groupInfo["entities"].append({
                    "chance" : self.read.int(),
                    "ids" : re.findall('....', self.read.charArray(groupInfo["posCount"]*4))
                })
    
    def readItemData(self):
        itemInfo = {
            "tableCount" : self.read.int(),
            "table" : []
        }
        for i in xrange(0,itemInfo["tableCount"]):
            tableInfo = {
                "tableNumber" : self.read.int(),
                "tableName" : self.read.string(),
                "setCount" : self.read.int(),
                "set" : []
            }
            for j in xrange(0,tableInfo["setCount"]):
                setInfo = {
                    "itemCount" : self.read.int(),
                    "items" : []
                }
                for k in xrange(0,setInfo["itemCount"]):
                    setInfo["item"].append({
                        "percentualChance" : self.read.int(),
                        "itemID" : self.read.charArray(4)
                    })
                    
                tableInfo["set"].append(setInfo)
                
            itemInfo["table"].append(tableInfo)
            
        return itemInfo
        
if __name__ == "__main__":
    import os
    import simplejson
    #this is where shit happens!
    filename = "input/war3map.w3i"
    wc3Info = WC3Info(filename)
    
    try:
        os.makedirs('./output')
    except OSError:
        pass
    with open("output/info.json", "w") as f:
        f.write(simplejson.dumps(wc3Info.info, sort_keys=True, indent=4 * ' '))