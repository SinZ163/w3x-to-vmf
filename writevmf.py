from read_w3e import ReadW3E
import traceback
import re
import os

def subInfo(template, id, x, x2, y, y2, z):
    toWrite = re.sub("~~ID~~", str(id), template)
    toWrite = re.sub("~~X~~", str(x), toWrite)
    toWrite = re.sub("~~X2~~", str(x2), toWrite)
    toWrite = re.sub("~~Y~~", str(y), toWrite)
    toWrite = re.sub("~~Y2~~", str(y2), toWrite)
    toWrite = re.sub("~~Z~~", str(z), toWrite)
    return toWrite
data = ReadW3E("input/war3map.w3e")

mapInfo = ""
vmfTemplate = {}

for fileName in ["header","footer","planeEntry"]:
    with open("template/"+fileName+".txt", "r") as f:
        vmfTemplate[fileName] = f.read()

try:
    os.makedirs('./output')
except OSError:
    pass
with open("output/output.vmf", "w") as f:
    f.write(vmfTemplate["header"])
    x = 0
    for x in xrange(data.mapInfo["width"]):
        curY = 0
        len = 1
        for y in xrange(data.mapInfo["height"]):
            index = y*data.mapInfo["height"] + x
            z = data.mapInfo["info"][index]["groundHeight"] - 8190
            
            #print("X: "+str(x))
            #print("Y: "+str(y))
            #print("Len: "+str(len))
            
            if y < data.mapInfo["height"] - 1:
                newIndex = (y+1)*data.mapInfo["height"] + x
                if data.mapInfo["info"][index]["groundHeight"] == data.mapInfo["info"][newIndex]["groundHeight"]:
                    if data.mapInfo["info"][index]["nibble1"] & 0xF == data.mapInfo["info"][newIndex]["nibble1"]  & 0xF:
                        #print("Height is same AND texture is same, lets reuse")
                        continue
                else:
                    curY = y
            print("Writing time")
            f.write(subInfo(vmfTemplate["planeEntry"],index+6,x,x+1,curY,y - curY+1,z))
            
    f.write(vmfTemplate["footer"])