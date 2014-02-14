from PIL import Image, ImageFont, ImageDraw

class TopDownViewer:         
    def __init__(self):
        
        self.textures = self.__texture__("ui/WC3 Art/ground",
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


        self.placeholder = Image.open("ui/WC3 Art/placeholder.tga")
        
        self.font = ImageFont.truetype("arial.ttf", 15)
        print "everything initiated"
        
    
    def createImage(self, mapData, debug={"validTile" : False, "invalidTile" : False, "height" : False,
                                        "ramp" : False, "water" : False, "blight" : False}):
        img = Image.new("RGB", (mapData.mapInfo["width"]*32, mapData.mapInfo["height"]*32))

        draw = ImageDraw.Draw(img)
        self.__work__(img, draw, mapData, debug)
        
        return img
        
    def __texture__(self, folder, textDict):
        textureInfo = {
            "textureDict" : textDict,
            "folder" : folder,
            "dict" : {}
        }
        for file in textDict:
            
            tile = Image.open(folder+"/"+file)
            minimap = textDict[file]
            width, height = tile.size
            subtile_list = []
            
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
                    
                    subtile_list.append((resized, averageBrightness))
            textureInfo["dict"][minimap] = subtile_list
            
        return textureInfo
    
    def averageColor(self, *args):
        print args
    
    def __work__(self, img, draw, mapData, debug):
        for x in xrange(mapData.mapInfo["width"]):
            for y in xrange(mapData.mapInfo["height"]):
                index = y*mapData.mapInfo["width"] + x
                
                tile = mapData.mapInfo["info"][index]
                
                
                tiletype = tile["groundTextureType"]
                type = mapData.mapInfo["groundTileSets"][tiletype]
                
                y = mapData.mapInfo["height"] - y-1
                
                if type in self.textures["dict"]:
                    #subindex = tile["textureDetails"]
                    subindex = 0
                    
                    try:
                        texture, brightness = self.textures["dict"][type][subindex] 
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
                    if debug["ramp"]:
                        #is it a ramp
                        if tile["flags"] & 1:
                            #top
                            draw.line(((x*32,y*32),(x*32+31,y*32)),fill=(0xFF,0,0))
                            #bottom
                            draw.line(((x*32,y*32+31),(x*32+31,y*32+31)),fill=(0xFF,0,0))
                            #left
                            draw.line(((x*32,y*32),(x*32, y*32+31)),fill=(0xFF,0,0))
                            #right
                            draw.line(((x*32+31,y*32),(x*32+31, y*32+31)),fill=(0xFF,0,0))
                    if debug["water"]:
                        if tile["flags"] & 4:
                            #top
                            draw.line(((x*32+1,y*32+1),(x*32+30,y*32+1)),fill=(0,0,0xFF))
                            #bottom
                            draw.line(((x*32+1,y*32+30),(x*32+30,y*32+30)),fill=(0,0,0xFF))
                            #left
                            draw.line(((x*32+1,y*32+1),(x*32+1, y*32+30)),fill=(0,0,0xFF))
                            #right
                            draw.line(((x*32+30,y*32+1),(x*32+30, y*32+30)),fill=(0,0,0xFF))
                    if debug["blight"]:
                        if tile["flags"] & 2:
                            #top
                            draw.line(((x*32+2, y*32+2),(x*32+29,y*32+2)), fill=(0xFF,0,0xFF))
                            #bottom
                            draw.line(((x*32+2,y*32+29),(x*32+29,y*32+29)),fill=(0xFF,0,0xFF))
                            #left
                            draw.line(((x*32+2,y*32+2),(x*32+2,y*32+29)),  fill=(0xFF,0,0xFF))
                            #right
                            draw.line(((x*32+29,y*32+2),(x*32+29,y*32+29)),fill=(0xFF,0,0xFF))
                            
                        
if __name__ == "__main__":
    from read_w3e import ReadW3E
    import sys
    debugSettings = {
        "invalidTile" : True,
        "validTile" : True,
        "ramp" : True,
        "height" : True,
        "water" : True,
        "blight" : True
    }
    image = TopDownViewer()
    img = image.createImage(ReadW3E(sys.argv[1]), debugSettings)
    img.save("ui/tmp/test.png", "PNG")
