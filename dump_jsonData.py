import traceback
import simplejson
from WC3MapObject import WC3Map

from lib.ReadFiletype.read_wts import read_WTS
from lib.ReadFiletype.read_object import (read_W3U, read_W3T, read_W3A,
                                          translate_info) 


# war3map.w3u for items
# war3map.w3a for abilities
# war3map.w3t for items


# INPUTPATH specifies the path to your w3x map.
# OUTPUTPATH specifies the output directory where 
# the json data should be stored. Leave empty to
# save in the current working directory.
INPUTPATH = "path_to_map"
OUTPUTPATH = "output_path"

#with open(inputPath, "rb") as f:
mpqHandle = open(INPUTPATH, "rb")
WarMap = WC3Map(mpqHandle, forceV1 = True)

try:
    item_file = WarMap.read_file("war3map.w3t")
except Exception as error:
    print "Couldn't extract item file:" +str(error)
    print
    item_file = None

try:
    ability_file = WarMap.read_file("war3map.w3a")
except Exception as error:
    print "Couldn't extract ability file:" +str(error)
    print
    ability_file = None

try:
    unit_file = WarMap.read_file("war3map.w3u")
except Exception as error:
    print "Couldn't extract unit file:" +str(error)
    print
    unit_file = None

try:
    trigger_file = WarMap.read_file("war3map.wts")
except Exception as error:
    print "Couldn't extract trigger string file:" +str(error)
    print "TRIGSTR resolving will not be available."
    trigger_file = None

mpqHandle.close()

if trigger_file != None:
    # We can resolve TRIGSTR strings according to
    # what is written in the wts file. 
    triggerDB = read_WTS(trigger_file)
else:
    # No TRIGSTR resolving. :(
    triggerDB = None


if item_file != None:
    itemData = read_W3T(item_file, triggerDB)
    
    translated_itemData = {"fileVersion" : itemData["fileVersion"],
                           "originalInfo" : translate_info(itemData["originalInfo"], "w3t"),
                           "customInfo" : translate_info(itemData["customInfo"], "w3t")}
    
    
    path = OUTPUTPATH+"war3map.w3t_itemData.json"
    with open(path, "w") as f:
        simplejson.dump(translated_itemData, fp = f, indent = " "*4)
    print "Wrote item data to '{0}'".format(path)
else:
    print "Did not dump any item data."
    
if ability_file != None:
    abilityData = read_W3A(ability_file, triggerDB)
    
    translated_abilityData = {"fileVersion" : itemData["fileVersion"],
                           "originalInfo" : translate_info(abilityData["originalInfo"], "w3a"),
                           "customInfo" : translate_info(abilityData["customInfo"], "w3a")}
    
    path = OUTPUTPATH+"war3map.w3a_abilityData.json"
    with open(path, "w") as f:
        simplejson.dump(translated_itemData, fp = f, indent = " "*4)
    print "Wrote ability data to '{0}'".format(path)
else:
    print "Did not dump any ability data."
    
if unit_file != None:
    unitData = read_W3U(unit_file, triggerDB)
    
    translated_unitData = {"fileVersion" : itemData["fileVersion"],
                           "originalInfo" : translate_info(unitData["originalInfo"], "w3u"),
                           "customInfo" : translate_info(unitData["customInfo"], "w3u")}
    
    path = OUTPUTPATH+"war3map.w3u_unitData.json"
    with open(path, "w") as f:
        simplejson.dump(translated_unitData, fp = f, indent = " "*4)
    print "Wrote unit data to '{0}'".format(path)
else:
    print "Did not dump any unit data."
    
print "Done!"



