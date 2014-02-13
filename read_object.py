import traceback #temp

class ObjectReader():
    from lib.DataReader import DataReader

    #These are the file extentions that have more reading
    OptionalInts = [
            "w3d",
            "w3a",
            "w3q"
    ]
    variableTypes = []
    def __init__(self, filename):
        self.filename = filename
        self.read = self.DataReader(filename)
        self.variableTypes = [
            self.read.int,
            self.read.float,
            self.read.float,
            self.read.string
        ]
        
        self.fileVersion = self.read.int()
        self.originalInfo = self.readTable()
        self.customInfo = self.readTable()
        
    def readMod(self):
        modInfo = {}
        modInfo["ID"] = self.read.charArray(4)
        varType = self.read.int()
        fileSplit = self.filename.split(".")
        if fileSplit[len(fileSplit)-1] in self.OptionalInts:
            modInfo["level"] = self.read.int()
            modInfo["pointer"] = self.read.int()
        modInfo["value"] = self.variableTypes[varType]()
        self.read.int() #verify / end thing
        return modInfo
    def readObject(self):
        objectData = {}
        objectData["oldID"] = self.read.charArray(4)
        objectData["newID"] = self.read.charArray(4)
        modCount = self.read.int()
        objectData["mods"] = []
        for i in xrange(modCount):
            objectData["mods"].append(self.readMod())
        return objectData
    def readTable(self):
        tmpLen = self.read.int()
        tmpInfo = []
        if tmpLen > 0:
            for i in xrange(tmpLen):
                tmpInfo.append(self.readObject())
        return tmpInfo
class TranslationHandle():
    def __init__(self, fileInfo):
        self.originalInfo = fileInfo
        fileSplit = fileInfo.filename.split(".")
        self.extention = fileSplit[len(fileSplit)-1]
        
        self.itemTable = {
            "icla" : "Classification",
            "unam" : "Name",
            "ides" : "Description",
            "utip" : "ToolTip", #iunno
            "utub" : "LongToolTip", #iunno
            "iabi" : "AbilityList",
            "iico" : "Icon",
            "igol" : "GoldCost",
            "ilum" : "LumberCost",
            "iusa" : "Usable",
            "iuse" : "Charges",
            "iper" : "Perishable",
            "isto" : "StockMax",
            "istr" : "StockRegen",
            "uhot" : "LegacyHotkey",
            "isst" : "StockStart",
            "ilev" : "Level",       #No idea
            "idro" : "Droppable",   
            "idrp" : "Drop",        #maybe IsDropped
            "ihtp" : "HP"
        }
        self.extentions = {
            "w3u" : {
                "name" : "Units"
            },
            "w3t" : {
                "name" : "Items",
                "function" : self.itemTranslation
            },
            "w3b" : {
                "name" : "Destructables"
            },
            "w3d" : {
                "name" : "Doodads"
            },
            "w3a" : {
                "name" : "Abilities"
            },
            "w3h" : {
                "name" : "Buffs"
            },
            "w3q" : {
                "name" : "Upgrades"
            }
        }
        try:
            self.info = self.extentions[self.extention]["function"]()
        except:
            #"bad SinZ, bad!" - SinZ 2014
            print(traceback.format_exc())
            
    def itemTranslation(self):
        itemTranslatedInfo = {}
        #THIS IS SO MESSY!!!! - SinZ 2014
        for i in xrange(len(self.originalInfo.customInfo)):
            tmpInfo = {}
            for j in xrange(len(self.originalInfo.customInfo[i]["mods"])):
                if self.originalInfo.customInfo[i]["mods"][j]["ID"] in self.itemTable:
                    tmpInfo[self.itemTable[self.originalInfo.customInfo[i]["mods"][j]["ID"]]] = self.originalInfo.customInfo[i]["mods"][j]["value"]
            itemTranslatedInfo[tmpInfo["Name"]] = tmpInfo
        return itemTranslatedInfo
if __name__ == "__main__":
    import simplejson
    import os
    filename = "input/war3map.w3t"
    fileInfo = ObjectReader(filename)
    transInfo = TranslationHandle(fileInfo)
    #Now to make a usable file
    #itemTranslation = {
    #    "icla" : "Classification",
    #    "unam" : "Name",
    #    "ides" : "Description",
    #    "utip" : "ToolTip", #iunno
    #    "utub" : "LongToolTip", #iunno
    #    "iabi" : "AbilityList",
    #    "iico" : "Icon",
    #    "igol" : "GoldCost",
    #    "ilum" : "LumberCost",
    #    "iusa" : "Usable",
    #    "iuse" : "Charges",
    #    "iper" : "Perishable",
    #    "isto" : "StockMax",
    #    "istr" : "StockRegen",
    #    "uhot" : "LegacyHotkey",
    #    "isst" : "StockStart",
    #    "ilev" : "Level",       #No idea
    #    "idro" : "Droppable",   
    #    "idrp" : "Drop",        #maybe IsDropped
    #    "ihtp" : "HP"
    #}
    #itemTranslatedInfo = {}
    #for i in xrange(len(fileInfo.customInfo)):
    #    tmpInfo = {}
    #    for j in xrange(len(fileInfo.customInfo[i]["mods"])):
    #        if fileInfo.customInfo[i]["mods"][j]["ID"] in itemTranslation:
    #            tmpInfo[translation[fileInfo.customInfo[i]["mods"][j]["ID"]]] = fileInfo.customInfo[i]["mods"][j]["value"]
    #    itemTranslatedInfo[tmpInfo["Name"]] = tmpInfo
        
    #Ok, lets write to json
    try:
        os.makedirs('./output')
    except OSError:
        pass
    with open("output/original.json", "w") as f:
        f.write(simplejson.dumps(fileInfo.originalInfo, sort_keys=True, indent=4 * ' '))
    with open("output/custom.json", "w") as f:
        f.write(simplejson.dumps(fileInfo.customInfo, sort_keys=True, indent=4 * ' '))
    #Now for translated files
    try:
        os.makedirs('./output/translated')
    except OSError:
        pass
    with open("output/translated/itemInfo.json","w") as f:
        f.write(simplejson.dumps(transInfo.info, sort_keys=True, indent=4 * ' '))
        #f.write(simplejson.dumps(itemTranslatedInfo, sort_keys=True, indent=4 * ' '))