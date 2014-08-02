import traceback #temp

import simplejson
from lib.DataReader import DataReader

def read_object(filehandle, filetype):
    readFile = {"w3u" : read_W3U,
                "w3t" : read_W3T,
                "w3b" : read_W3B,
                "w3d" : read_W3D,
                "w3a" : read_W3A,
                "w3h" : read_W3H,
                "w3q" : read_W3Q}
    
    #read = DataReader(filehandle)
    
    data = readFile[filetype](filehandle)
    return data
    

def read_W3U(filehandle):
    data = __read_generic_object__(filehandle, "w3u")
    return data

def read_W3T(filehandle):
    data = __read_generic_object__(filehandle, "w3t")
    return data

def read_W3B(filehandle):
    data = __read_generic_object__(filehandle, "w3b")
    return data

def read_W3D(filehandle):
    data = __read_generic_object__(filehandle, "w3d")
    return data

def read_W3A(filehandle):
    data = __read_generic_object__(filehandle, "w3a")
    return data

def read_W3H(filehandle):
    data = __read_generic_object__(filehandle, "w3h")
    return data

def read_W3Q(filehandle):
    data = __read_generic_object__(filehandle, "w3q")
    return data
    

#class ObjectReader():
#    #These are the file extentions that have more reading
#    OptionalInts = [
#            "w3d",
#            "w3a",
#            "w3q"
#    ]
#    variableTypes = []
    
def __read_generic_object__(filehandle, filetype):
    read = DataReader(filehandle)
    #variableTypes = [
    #    read.int,
    #    read.float,
    #    read.float,
    #    read.string
    #]
    
    fileVersion = read.int()
    originalInfo = __readTable__(read, filetype)
    customInfo = __readTable__(read, filetype)
    
    data = {"fileVersion" : fileVersion,
            "originalInfo" : originalInfo,
            "customInfo" : customInfo}
    
    return data
    
def __readTable__(read, filetype):
    objectsTable = []
    
    objectsTable_len = read.int()
    if objectsTable_len > 0:
        for i in xrange(objectsTable_len):
            object = __readObject__(read, filetype)
            objectsTable.append(object)
            
    return objectsTable

def __readObject__(read, filetype):
    objectData = {}
    
    objectData["oldID"] = read.charArray(4)
    objectData["newID"] = read.charArray(4)
    objectData["mods"] = []
    
    modCount = read.int()
    for i in xrange(modCount):
        mod = __readMod__(read, filetype)
        objectData["mods"].append(mod)
        
    return objectData

def __readMod__(read, filetype):
    modInfo = {}
    modInfo["ID"] = read.charArray(4)
    varType = read.int()
    
    if filetype in ("w3d", "w3a", "w3q"):
        modInfo["level"] = read.int()
        modInfo["pointer"] = read.int()
    
    if varType == 0:
        val = read.int()
    elif varType == 1 or varType == 2:
        val = read.float()
    elif varType == 3:
        val = read.string()
    else:
        raise RuntimeError("Data Type for {0} (file type: {1}) is {2}".format(modInfo["ID"],
                                                                              filetype, 
                                                                              varType))
    modInfo["value"] = val
    read.int() #verify / end thing
    
    return modInfo



#
# A dict that translates the short 4-character IDs
# into full names.
#

infoFile = open("object_ids.json", "r")
infoTable = simplejson.load(infoFile)
infoFile.close()

#
# Full names of the 3-character extensions
#
extentions = {
    "w3u" : "Units",
    "w3t" : "Items",
    "w3b" : "Destructables",
    "w3d" : "Doodads",
    "w3a" : "Abilities",
    "w3h" : "Buffs",
    "w3q" : "Upgrades"
}
    
#class TranslationHandle():
#    def __init__(self, fileInfo):

def translate_info(infodata, filetype, strict = True):
    if filetype in ("w3u", "w3t", "w3a"):
        info = __dataTranslation__(infodata)
        return info
    
    else:
        if strict:
            raise RuntimeError("No translation available for the following "
                               "extension: {0}".format(filetype))
        else:
            return None
        
def __dataTranslation__(infodata):
    dataTranslatedInfo = {}
    #THIS IS SO MESSY!!!! - SinZ 2014
    # THIS IS FAR TOO MESSY FOR MY TASTE!!! - Yoshi2 2014
    unknownCount = 0
    
    for i, objectDict in enumerate(infodata):
        tmpInfo = {}
        
        for mod in objectDict["mods"]:
            modID = mod["ID"]
            if modID.upper() in infoTable:
                translated_modID = infoTable[modID.upper()] 
                modValue = mod["value"]
                
                tmpInfo[translated_modID] = modValue
        if "Name" in tmpInfo:
            dataTranslatedInfo[tmpInfo["Name"]] = tmpInfo
        else:
            unknownName = "UnknownName_{0}".format(unknownCount)
            dataTranslatedInfo[unknownName] = tmpInfo
            
            unknownCount += 1
            
    return dataTranslatedInfo
    
    
