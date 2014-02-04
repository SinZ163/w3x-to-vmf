#w3u = Units
#w3t = Items
#w3b = Destructables
#w3d = Doodads
#w3a = Abilities
#w3h = Buffs
#w3q = Upgrades

#ok, lets open a file

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
        if filename.split(".")[1] in self.OptionalInts:
            modInfo["level"] = self.read.int()
            modInfo["pointer"] = self.read.int()
        print(varType)
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
if __name__ == "__main__":
    import simplejson
    import os
    filename = "input/war3map.w3t"
    fileInfo = ObjectReader(filename)
    #Now to make a usable file
    translation = {
        "icla" : "Classification",
        "unam" : "Name",
        "ides" : "Description",
        "utip" : "ShopName", #iunno
        "utub" : "ToolTip", #iunno
        "iabi" : "Ability",
        "iico" : "Icon",
        "igol" : "GoldCost",
        "ilum" : "LumberCost",
        "iusa" : "HasActive"
    }
    translatedInfo = {}
    for i in xrange(len(fileInfo.customInfo)):
        tmpInfo = {}
        for j in xrange(len(fileInfo.customInfo[i]["mods"])):
            if fileInfo.customInfo[i]["mods"][j]["ID"] in translation:
                tmpInfo[translation[fileInfo.customInfo[i]["mods"][j]["ID"]]] = fileInfo.customInfo[i]["mods"][j]["value"]
        translatedInfo[tmpInfo["Name"]] = tmpInfo
        
    #Ok, lets write to json
    try:
        os.makedirs('./output')
    except OSError:
        pass
    with open("output/original.json", "w") as f:
        f.write(simplejson.dumps(fileInfo.originalInfo, sort_keys=True, indent=4 * ' '))
    with open("output/custom.json", "w") as f:
        f.write(simplejson.dumps(fileInfo.customInfo, sort_keys=True, indent=4 * ' '))
    with open("output/translated.json","w") as f:
        f.write(simplejson.dumps(translatedInfo, sort_keys=True, indent=4 * ' '))