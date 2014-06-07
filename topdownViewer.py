import simplejson

from PIL import Image, ImageFont, ImageDraw


class TopDownViewer:
    textureLoc = "ui/WC3 Art/ground"
    textures = {
        "Alvd" : "Ashen_Leaves.tga",
        "Idrt" : "Ice_Dirt.tga",
        "Idki" : "Ice_DarkIce.tga",
        "Idtr" : "Ice_DirtRough.tga",
        "Iice" : "Ice_Ice.tga",
        "Irbk" : "Ice_RuneBricks.tga",
        "Isnw" : "Ice_Snow.tga",
        "Ldrt" : "Lords_Dirt.tga",
        "Ldro" : "Lords_DirtRough.tga",
        "Lgrs" : "Lords_Grass.tga",
        "Lgrd" : "Lords_GrassDark.tga",
        "Lrok" : "Lords_Rock.tga",
        "Qcbp" : "VillageFall_CobblePath.tga",
        "Vcrp" : "Village_Crops.tga",
        "Vgrs" : "Village_GrassShort.tga",
        "Wdro" : "Lordw_DirtRough.tga",
        "Wdrt" : "Lordw_Dirt.tga",
        "Wgrs" : "Lordw_Grass.tga",
        "Wrok" : "Lordw_Rock.tga",
        "Wsng" : "Lordw_SnowGrass.tga",
        "Wsnw" : "Lordw_Snow.tga",
        "Ydtr" : "City_Dirt.tga",
        "Yblm" : "City_BlackMarble.tga",
        "Ybtl" : "City_BrickTiles.tga",
        "Ysqd" : "City_SquareTiles.tga",
        "Yrtl" : "City_RoundTiles.tga",
        "Ygsb" : "City_Grass.tga",
        "Yhdg" : "City_GrassTrim.tga",
        "Ywmb" : "City_WhiteMarble.tga",
        "Zdrt" : "Ruins_Dirt.tga",
        "Zdtr" : "Ruins_DirtRough.tga",
        "Zdrg" : "Ruins_DirtGrass.tga",
        "Zbks" : "Ruins_SmallBricks.tga",
        "Zsan" : "Ruins_Sand.tga",
        "Zbkl" : "Ruins_LargeBricks.tga",
        "Ztil" : "Ruins_RoundTiles.tga",
        "Zgrs" : "Ruins_Grass.tga",
        "Zvin" : "Ruins_GrassDark.tga"        
    }
    def __init__(self):
        
        '''self.textures = self.__texture__("ui/WC3 Art/ground",
                   {"Ashen_Leaves.tga" : "Alvd",
                    "City_Dirt.tga" : "Ydrt",
                    "City_DirtRough.tga" : "Ydtr",
                    "City_BlackMarble.tga" : "Yblm",
                    "City_BrickTiles.tga" : "Ybtl",
                    "City_SquareTiles.tga" : "Ysqd",
                    "City_RoundTiles.tga" : "Yrtl",
                    "City_Grass.tga" : "Ygsb",
                    "City_GrassTrim.tga" : "Yhdg",
                    "City_WhiteMarble.tga" : "Ywmb",
                    "Ice_Dirt.tga" : "Idrt",
                    "Ice_DarkIce.tga" : "Idki",
                    "Ice_DirtRough.tga" : "Idtr",
                    "Ice_Ice.tga" : "Iice",
                    "Ice_RuneBricks.tga" : "Irbk",
                    "Ice_Snow.tga" : "Isnw",
                    "Lords_Dirt.tga" : "Ldrt",
                    "Lords_DirtRough.tga" : "Ldro",
                    "Lords_Grass.tga" : "Lgrs",
                    "Lords_GrassDark.tga" : "Lgrd",
                    "Lords_Rock.tga" : "Lrok",
                    "Lordw_Dirt.tga" : "Wdrt",
                    "Lordw_DirtRough.tga" : "Wdro",
                    "Lordw_SnowGrass.tga" : "Wsng",
                    "Lordw_Rock.tga" : "Wrok",
                    "Lordw_Grass.tga" : "Wgrs",
                    "Lordw_Snow.tga" : "Wsnw",
                    "Ruins_Dirt.tga" : "Zdrt",
                    "Ruins_DirtRough.tga" : "Zdtr",
                    "Ruins_DirtGrass.tga" : "Zdrg",
                    "Ruins_SmallBricks.tga" : "Zbks",
                    "Ruins_Sand.tga" : "Zsan",
                    "Ruins_LargeBricks.tga" : "Zbkl",
                    "Ruins_RoundTiles.tga" : "Ztil",
                    "Ruins_Grass.tga" : "Zgrs",
                    "Ruins_GrassDark.tga" : "Zvin",
                    "Village_Crops.tga" : "Vcrp",
                    "Village_GrassShort.tga" : "Vgrs",
                    "VillageFall_CobblePath.tga" : "Qcbp"})
        '''

        self.placeholder = Image.open("ui/WC3 Art/placeholder.tga")
        
        self.font = ImageFont.truetype("arial.ttf", 15)
        print "everything initiated"
        
    
    def createImage(self, mapData, debug={"validTile" : False, "invalidTile" : False, "height" : False,
                                        "ramp" : False, "water" : False, "blight" : False}):
        img = Image.new("RGB", (mapData.mapInfo["width"]*32, mapData.mapInfo["height"]*32))
        self.textureList = self.__texture__(mapData.mapInfo["groundTileSets"])
        draw = ImageDraw.Draw(img)
        self.__work__(img, draw, mapData, debug)
        
        self.__drawTrees_(draw, mapData)
        self.cleanup()
        
        return img
    
    def cleanup(self):
        del self.textureList
    
    def __drawTrees_(self, draw, mapData):
        try:
            treeDump = simplejson.load(open("output/treeDump.json"))
        except:
            # No trees will be drawn today because the file is missing.
            return
        
        for tree in treeDump:
            draw.rectangle(((((tree["x"] - mapData.mapInfo["offsetX"]) / 4) - 2, (mapData.mapInfo["height"]*32 - (((tree["y"]- mapData.mapInfo["offsetY"]) / 4)-2))),
                             ((tree["x"] - mapData.mapInfo["offsetX"]) / 4) + 2, (mapData.mapInfo["height"]*32 - (((tree["y"]- mapData.mapInfo["offsetY"]) / 4)+2))),
                               fill=(0,0,0), outline=(0,0,0))
    def __texture__(self, groundTileSets):
        info = []
        for tileset in groundTileSets:
            if tileset in self.textures:               
                textureInfo = []
                tile = Image.open(self.textureLoc+"/"+self.textures[tileset])
                width, height = tile.size
                for ix in xrange(width/64):
                    for iy in xrange(height/64):
                        
                        averageBrightness = False
                        
                        ix2, iy2 = ix+1, iy+1
                        cropped = tile.crop((ix*64, iy*64, ix2*64, iy2*64))

                        resized = cropped.resize((32,32), Image.ANTIALIAS)
                        
                        # pixelData should contain 4 values: Red, Green, Blue and Alpha.
                        # We only need the colour values.
                        # We calculate the grayscale color according to the following page:
                        # http://en.wikipedia.org/wiki/Grayscale#Colorimetric_.28luminance-preserving.29_conversion_to_grayscale
                        # Y = 0.2126*R + 0.7152*G + 0.0722*B
                        for pixelData in resized.getdata(): 
                            if averageBrightness == False:
                                averageBrightness = (pixelData[0]*0.2126 + pixelData[1]*0.7152 + pixelData[2]*0.0722)
                            else:
                                currentBrightness = (pixelData[0]*0.2126 + pixelData[1]*0.7152 + pixelData[2]*0.0722)
                                averageBrightness = (averageBrightness+currentBrightness) / 2.0
                        
                        # We round the number and convert it to an integer that
                        # represents the average brightness somewhat accurately.
                        averageBrightness = int(round(averageBrightness))
                        
                        textureInfo.append((resized, averageBrightness))
                info.append(textureInfo)
            else:
                info.append(([self.placeholder],-1))
        return info
    
    def averageColor(self, *args):
        print args
        
    def drawFlag(self, draw, x, y, ring, colour, size=32):
        topLeft = (x*size+ring,y*size+ring)
        topRight = (x*size+(size-ring-1),y*size+ring)
        botLeft = (x*size+ring,y*size+(size-ring-1))
        botRight = (x*size+(size-ring-1),y*size+(size-ring-1))
        #top
        draw.line((topLeft,topRight),fill=colour)
        #bot
        draw.line((botLeft,botRight),fill=colour)
        #left
        draw.line((topLeft,botLeft),fill=colour)
        #right
        draw.line((topRight,botRight),fill=colour)
        
    def __work__(self, img, draw, mapData, debug):
        for x in xrange(mapData.mapInfo["width"]):
            for y in xrange(mapData.mapInfo["height"]):
                index = y*mapData.mapInfo["width"] + x
                
                tile = mapData.mapInfo["info"][index]
                
                
                tiletype = tile["groundTextureType"]
                #used only for writing text
                type = mapData.mapInfo["groundTileSets"][tiletype]
                
                y = mapData.mapInfo["height"] - y-1
                
                #subindex = tile["textureDetails"]
                subindex = 0
                
                try:
                    #texture, brightness = self.textures["dict"][type][subindex]
                    texture, brightness = self.textureList[tiletype][subindex]
                    if brightness == -1: #is it placeholder or not
                        thisShouldErrorIntoExcept("hopefully")
                    img.paste(texture, (x*32, y*32))
                    
                    colorMod = 127.0/float(brightness)
                    
                    if debug["validTile"]:
                        draw.text((x*32+2, y*32+1), str(hex(subindex)), font = self.font, fill = (0, int(255*colorMod), int(33*colorMod)))
                        draw.text((x*32+2, y*32+14), str(type), font = self.font, fill = (int(140*colorMod), int(140*colorMod), int(140*colorMod), 200))
                        #draw.text((x*32+1, y*32), str(tile["layerHeight"]), font = self.font, fill = (0, 255, 33))
                except:
                    img.paste(self.placeholder, (x*32, y*32))
                    if debug["invalidTile"]:
                        draw.text((x*32+1, y*32), str(hex(subindex)), font = self.font, fill = (255, 0, 33))
                        draw.text((x*32+1, y*32+15), str(type), font = self.font, fill = (140, 140, 140, 200))
                if debug["ramp"] and tile["flags"] & 1:
                    self.drawFlag(draw, x, y, 0, (0xFF,0,0),size=32)
                if debug["water"] and tile["flags"] & 4:
                    self.drawFlag(draw, x, y, 1, (0,0,0xFF),size=32)
                if debug["blight"] and tile["flags"] & 2:
                    self.drawFlag(draw, x, y, 2, (0xFF,0,0xFF),size=32)
               
                        
if __name__ == "__main__":
    import sys
    
    from lib.ReadFiletype_Scripts.read_w3e import ReadW3E
    
    debugSettings = {
        "invalidTile" : True,
        "validTile" : False,
        "ramp" : False,
        "height" : False,
        "water" : True,
        "blight" : False
    }
    
    image = TopDownViewer()
    img = image.createImage(ReadW3E(sys.argv[1]), debugSettings)
    img.save("ui/tmp/test.png", "PNG")
