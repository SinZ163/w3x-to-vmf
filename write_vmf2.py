from lib.ReadFiletype.read_w3e import read_W3E
from lib.ReadFiletype.read_doo import read_doodad

import simplejson #TEMP

def getIndex(x, y, width):
    return y*width + x
def getHeight(data, x, y):
    index = getIndex(x,y,data["width"])
    vertex = data["info"][index]
    #return vertex["groundHeight"] - 0x2000 + (vertex["layerHeight"] - 2)*0x200 / 4 + 512 #512 is probably temp
    return (vertex["layerHeight"] - 2)*0x200 / 4 + 512

def coordToDota(value, dimension):
    return (-(dimension) / 2 + value)*128
def write(f, indent, string):
    f.write(indent*"    " + string + "\n")
    
wc3fileName = "input/TreeTag,TFI_5.13 (1).w3x-war3map.w3e" #TODO: Replace with better system
doodadFileName = "input/TreeTag,TFI_5.13 (1).w3x-war3map.doo"
dotafileName = "output/war3map_treetag_t.vmf" # ^
print("Starting up...")

with open(wc3fileName, "rb") as f:
    wc3_mapinfo = read_W3E(f)
    print("Making a map that will be:")
    print(" {x}x{y}".format(x=wc3_mapinfo["width"]*128,y=wc3_mapinfo["height"]*128))
    print(" contain {0} textures*".format(len(wc3_mapinfo["groundTileSets"])))
    print(" and therefor, each texture will be {0} different".format(256.0/len(wc3_mapinfo["groundTileSets"])))
    with open(dotafileName, "w") as f:
        indent = 0
        f.write("""cameras
{
}
cordon
{
    "mins" "(99999 99999 99999)"
    "maxs" "(-99999 -99999 -99999)"
    "active" "0"
}
world
{
    "classname" "worldspawn"
    "spawnflags" "0"
    "skyname" "sky_dotasky_01"
    "mapversion" "0"
    "id" "0"
""")
        indent = 1
        id = 1
        for y in xrange(0, wc3_mapinfo["height"], 16):
            for x in xrange(0, wc3_mapinfo["width"], 16):
                if x == 0 or y == 0:
                    continue
                print(str(x) + " |  " + str(y))
                write(f, indent, "solid")
                write(f, indent, "{")
                indent += 1
                write(f, indent, '"id" "{}"'.format(id))
                id += 1
                write(f, indent, "side")
                write(f, indent, "{")
                indent += 1
                #We are now inside side
                write(f, indent, '"id" "{}"'.format(id))
                id += 1
                write(f, indent, '"plane" "({} {} 512) ({} {} 512) ({} {} 512)"'.format(coordToDota(x-16, wc3_mapinfo["width"]), coordToDota(y-16,wc3_mapinfo["height"]), 
                                                                                  coordToDota(x-16, wc3_mapinfo["width"]), coordToDota(y,wc3_mapinfo["height"]),
                                                                                  coordToDota(x, wc3_mapinfo["width"]), coordToDota(y,wc3_mapinfo["height"])
                                                                                 ))
                write(f, indent, '"material" "materials/blends/mod_architec123ture_example_000"')
                write(f, indent, '"uaxis" "[1 0 0 0] 0.25"') #I have no idea what I'm doing
                write(f, indent, '"vaxis" "[0 -1 0 0] 0.25"') # ^
                write(f, indent, '"rotation" "0"') #Why is this even in the format, its just a summary of the above two fields
                write(f, indent, '"lightmapscale" "16"')
                write(f, indent, '"smoothing_groups" "0"')

                write(f, indent, "dispinfo")
                write(f, indent, "{")
                indent += 1
                #We are now inside dispinfo
                write(f, indent, '"power" "4"')
                write(f, indent, '"startposition" "[{} {} 512]"'.format(coordToDota(x-16, wc3_mapinfo["width"]), coordToDota(y-16,wc3_mapinfo["height"])))
                write(f, indent, '"elevation" "0"')
                write(f, indent, '"subdiv" "0"')
                write(f, indent, "normals")
                write(f, indent, "{")
                indent += 1
                #We are now inside normals
                for i in xrange(17):
                    write(f, indent, '"row{}" "{}"'.format(i, ("0 0 1 "*17)[:-1]))
                indent -=1
                write(f, indent, "}")
                #we are back inside dispinfo

                write(f, indent, "distances")
                write(f, indent, "{")
                indent += 1
                #we are now inside distances
                for dy in xrange(17):
                    values = []
                    for dx in xrange(17):
                        values.append(str(getHeight(wc3_mapinfo, x - 16 + dx, y - 16 + dy)))
                    write(f, indent, '"row{}" "{}"'.format(dy, " ".join(values)))

                indent -= 1
                write(f, indent, "}")
                #We are back inside dispinfo

                write(f, indent, "offsets")
                write(f, indent, "{")
                indent += 1
                #we are now inside offsets
                for i in xrange(17):
                    write(f, indent, '"row{}" "{}"'.format(i, ("0 0 0 "*17)[:-1]))
                indent -= 1
                write(f, indent, "}")
                #we are back inside dispinfo

                write(f, indent, "offset_normals") #TODO: figure out wtf this is
                write(f, indent, "{")
                indent += 1
                #We are now inside normals
                for i in xrange(17):
                    write(f, indent, '"row{}" "{}"'.format(i, ("0 0 1 "*17)[:-1]))
                indent -=1
                write(f, indent, "}")
                #we are back inside dispinfo

                write(f, indent, "alphas") #TODO: Actually do this?
                write(f, indent, "{")
                indent += 1
                #We are now inside normals
                for i in xrange(17):
                    values = []
                    for j in xrange(17):
                        vertex = wc3_mapinfo["info"][getIndex(x-16+i,y-16+j,wc3_mapinfo["width"])] #i and j might be the wrong way around
                        values.append(str(256/len(wc3_mapinfo["groundTileSets"]) * vertex["groundTextureType"]))
                    write(f, indent, '"row{}" "{}"'.format(i, " ".join(values)))
                indent -=1
                write(f, indent, "}")
                #we are back inside dispinfo

                write(f, indent, "triangle_tags") #TODO: Actually do this?
                write(f, indent, "{")
                indent += 1
                #We are now inside normals
                for i in xrange(16):
                    write(f, indent, '"row{}" "{}"'.format(i, ("9 "*32)[:-1]))
                indent -=1
                write(f, indent, "}")
                #we are back inside dispinfo

                write(f, indent, "allowed_verts") #TODO: Actually do this?
                write(f, indent, "{")
                indent += 1
                #We are now inside normals
                write(f, indent, '"10" "{}"'.format(("-1 "*10)[:-1]))
                indent -=1
                write(f, indent, "}")
                #we are back inside dispinfo

                indent -= 1
                write(f, indent, '}')
                #We have just left dispinfo, and back in side
                
                indent -= 1
                write(f, indent, '}')
                #We have left side, and are in the solid.

                ###
                ### Bottom Side
                ###

                write(f, indent, "side")
                write(f, indent, "{")
                indent += 1
                #We are now inside side
                write(f, indent, '"id" "{}"'.format(id))
                id += 1
                write(f, indent, '"plane" "({} {} 0) ({} {} 0) ({} {} 0)"'.format(coordToDota(x-16, wc3_mapinfo["width"]), coordToDota(y-16,wc3_mapinfo["height"]), 
                                                                                  coordToDota(x, wc3_mapinfo["width"]), coordToDota(y-16,wc3_mapinfo["height"]),
                                                                                  coordToDota(x, wc3_mapinfo["width"]), coordToDota(y,wc3_mapinfo["height"])
                                                                                 ))
                write(f, indent, '"material" "nature/grass_03"')
                write(f, indent, '"uaxis" "[1 0 0 0] 0.25"') #I have no idea what I'm doing
                write(f, indent, '"vaxis" "[0 -1 0 0] 0.25"') # ^
                write(f, indent, '"rotation" "0"') #Why is this even in the format, its just a summary of the above two fields
                write(f, indent, '"lightmapscale" "16"')
                write(f, indent, '"smoothing_groups" "0"')
                indent -= 1
                write(f, indent, '}')
                #We have left side, and are in the solid.

                ###
                ### Left Side
                ###

                write(f, indent, "side")
                write(f, indent, "{")
                indent += 1
                #We are now inside side
                write(f, indent, '"id" "{}"'.format(id))
                id += 1
                write(f, indent, '"plane" "({} {} 512) ({} {} 512) ({} {} 0)"'.format(coordToDota(x-16, wc3_mapinfo["width"]), coordToDota(y,wc3_mapinfo["height"]), 
                                                                                  coordToDota(x-16, wc3_mapinfo["width"]), coordToDota(y-16,wc3_mapinfo["height"]),
                                                                                  coordToDota(x-16, wc3_mapinfo["width"]), coordToDota(y-16,wc3_mapinfo["height"])
                                                                                 ))
                write(f, indent, '"material" "nature/grass_04"')
                write(f, indent, '"uaxis" "[0 1 0 0] 0.25"') #I have no idea what I'm doing
                write(f, indent, '"vaxis" "[0 0 -1 0] 0.25"') # ^
                write(f, indent, '"rotation" "0"') #Why is this even in the format, its just a summary of the above two fields
                write(f, indent, '"lightmapscale" "16"')
                write(f, indent, '"smoothing_groups" "0"')
                indent -= 1
                write(f, indent, '}')
                #We have left side, and are in the solid.

                ###
                ### Right Side
                ###

                write(f, indent, "side")
                write(f, indent, "{")
                indent += 1
                #We are now inside side
                write(f, indent, '"id" "{}"'.format(id))
                id += 1
                write(f, indent, '"plane" "({} {} 0) ({} {} 0) ({} {} 512)"'.format(coordToDota(x, wc3_mapinfo["width"]), coordToDota(y,wc3_mapinfo["height"]), 
                                                                                  coordToDota(x, wc3_mapinfo["width"]), coordToDota(y-16,wc3_mapinfo["height"]),
                                                                                  coordToDota(x, wc3_mapinfo["width"]), coordToDota(y-16,wc3_mapinfo["height"])
                                                                                 ))
                write(f, indent, '"material" "nature/grass_05"')
                write(f, indent, '"uaxis" "[0 1 0 0] 0.25"') #I have no idea what I'm doing
                write(f, indent, '"vaxis" "[0 0 -1 0] 0.25"') # ^
                write(f, indent, '"rotation" "0"') #Why is this even in the format, its just a summary of the above two fields
                write(f, indent, '"lightmapscale" "16"')
                write(f, indent, '"smoothing_groups" "0"')
                indent -= 1
                write(f, indent, '}')
                #We have left side, and are in the solid.

                ###
                ### Back Side
                ###

                write(f, indent, "side")
                write(f, indent, "{")
                indent += 1
                #We are now inside side
                write(f, indent, '"id" "{}"'.format(id))
                id += 1
                write(f, indent, '"plane" "({} {} 512) ({} {} 512) ({} {} 0)"'.format(coordToDota(x, wc3_mapinfo["width"]), coordToDota(y,wc3_mapinfo["height"]), 
                                                                                  coordToDota(x-16, wc3_mapinfo["width"]), coordToDota(y,wc3_mapinfo["height"]),
                                                                                  coordToDota(x-16, wc3_mapinfo["width"]), coordToDota(y,wc3_mapinfo["height"])
                                                                                 ))
                write(f, indent, '"material" "nature/grass_06"')
                write(f, indent, '"uaxis" "[1 0 0 0] 0.25"') #I have no idea what I'm doing
                write(f, indent, '"vaxis" "[0 0 -1 0] 0.25"') # ^
                write(f, indent, '"rotation" "0"') #Why is this even in the format, its just a summary of the above two fields
                write(f, indent, '"lightmapscale" "16"')
                write(f, indent, '"smoothing_groups" "0"')
                indent -= 1
                write(f, indent, '}')
                #We have left side, and are in the solid.

                ###
                ### Front Side
                ###

                write(f, indent, "side")
                write(f, indent, "{")
                indent += 1
                #We are now inside side
                write(f, indent, '"id" "{}"'.format(id))
                id += 1
                write(f, indent, '"plane" "({} {} 0) ({} {} 0) ({} {} 512)"'.format(coordToDota(x, wc3_mapinfo["width"]), coordToDota(y-16,wc3_mapinfo["height"]), 
                                                                                  coordToDota(x-16, wc3_mapinfo["width"]), coordToDota(y-16,wc3_mapinfo["height"]),
                                                                                  coordToDota(x-16, wc3_mapinfo["width"]), coordToDota(y-16,wc3_mapinfo["height"])
                                                                                 ))
                write(f, indent, '"material" "nature/grass_07"')
                write(f, indent, '"uaxis" "[1 0 0 0] 0.25"') #I have no idea what I'm doing
                write(f, indent, '"vaxis" "[0 0 -1 0] 0.25"') # ^
                write(f, indent, '"rotation" "0"') #Why is this even in the format, its just a summary of the above two fields
                write(f, indent, '"lightmapscale" "16"')
                write(f, indent, '"smoothing_groups" "0"')
                indent -= 1
                write(f, indent, '}')
                #We have left side, and are in the solid.

                indent -= 1
                write(f, indent, '}')
                #We have left solid, and are in the world.
        indent -= 1
        write(f, indent, '}')
        #We have left world, and are in the void.
        doodadConversion = {
            "WTst" : "ent_dota_tree"
        }
        #Time for some doodads!
        wc3_dooinfo = read_doodad(doodadFileName)
        with open("output/newTreeInfo.json", "w") as g:
            g.write(simplejson.dumps(wc3_dooinfo, sort_keys=True, indent=4 * ' '))
        for treeInfo in wc3_dooinfo["trees"]:
            write(f, indent, "entity")
            write(f, indent, "{")
            indent += 1
            #We are now inside entity
            write(f, indent, '"id" "{}"'.format(id))
            id += 1
            if treeInfo["treeID"] in doodadConversion:
                write(f, indent, '"classname" "{}"'.format(doodadConversion[treeInfo["treeID"]]))
            else:
                write(f, indent, '"classname" "info_target"')
            write(f, indent, '"spawnflags" "0"')
            write(f, indent, '"origin" "{x} {y} {z}"'.format(**treeInfo["coord"]))
            write(f, indent, '"targetname" ""')
            indent -=1
            write(f, indent, "}")
            #We have left world, and are in the void.