class TopDownViewer:
    from PIL import Image, ImageFont, ImageDraw         
    def __init__(self, mapInfo, debug={"validTile" : False, "invalidTile" : False, "height" : False, "ramp" : False, "water" : False, "blight" : False}):
        self.debug = debug
        self.textures = self.Texture("ui/WC3 Art/ground",
                   {"Ashen_Leaves.tga" : "Alvd",
                    "City_DirtRough.tga" : "Ydtr",
                    "Ice_Dirt.tga" : "Idrt",
                    "Ice_DarkIce.tga" : "Idki",
                    "Ice_DirtRough.tga" : "Idtr",
                    "Ice_Ice.tga" : "Iice",
                    "Ice_RuneBricks.tga" : "Irbk",
                    "Ice_Snow.tga" : "Isnw",
                    "Lordw_Dirt.tga" : "Wdrt",
                    "Lordw_DirtRough.tga" : "Wdro",
                    "Lordw_SnowGrass.tga" : "Wsng",
                    "Lordw_Rock.tga" : "Wrok",
                    "Lordw_Grass.tga" : "Wgrs",
                    "Lordw_Snow.tga" : "Wsnw"})


        self.placeholder = self.Image.open("ui/WC3 Art/placeholder.tga")
        
        self.font = self.ImageFont.truetype("arial.ttf", 15)
        self.data = mapInfo
        self.img = self.Image.new("RGB", (self.data.mapInfo["width"]*32, self.data.mapInfo["height"]*32))

        self.draw = self.ImageDraw.Draw(self.img)
        self.work()
    def Texture(self, folder, textDict):
        textureInfo = {
            "textureDict" : textDict,
            "folder" : folder,
            "dict" : {}
        }
        for file in textDict:
            tile = self.Image.open(folder+"/"+file)
            minimap = textDict[file]
            width, height = tile.size
            subtile_list = []
            for ix in range(width/64):
                for iy in range(height/64):
                    ix2, iy2 = ix+1, iy+1
                    cropped = tile.crop((ix*64, iy*64, ix2*64, iy2*64))
                    subtile_list.append(cropped.resize((32,32)))
                    
            textureInfo["dict"][minimap] = subtile_list
            
        return textureInfo
    def work(self):
        for x in xrange(self.data.mapInfo["width"]):
            for y in xrange(self.data.mapInfo["height"]):
                index = y*self.data.mapInfo["height"] + x
                
                tile = self.data.mapInfo["info"][index]
                
                
                tiletype = tile["groundTextureType"]
                type = self.data.mapInfo["groundTileSets"][tiletype]
                
                y = self.data.mapInfo["height"] - y-1
                
                if type in self.textures["dict"]:
                    #subindex = tile["textureDetails"]
                    subindex = 0
                    
                    try:
                        self.img.paste(self.textures["dict"][type][subindex], (x*32, y*32))#
                        #bla = str(bin(subindex))[2:]
                        #print bla.zfill(8)
                        if self.debug["validTile"]:
                            self.draw.text((x*32+1, y*32), str(hex(subindex)), font = self.font, fill = (0, 255, 33))
                            self.draw.text((x*32+1, y*32+15), str(type), font = self.font, fill = (140, 140, 140, 200))
                    except:
                        #pass
                        self.img.paste(self.placeholder, (x*32, y*32))
                        if self.debug["invalidTile"]:
                            self.draw.text((x*32+1, y*32), str(hex(subindex)), font = self.font, fill = (255, 0, 33))
                            self.draw.text((x*32+1, y*32+15), str(type), font = self.font, fill = (140, 140, 140, 200))
                    if self.debug["ramp"]:
                        #is it a ramp
                        if tile["flags"] & 1:
                            #top
                            self.draw.line(((x*32,y*32),(x*32+31,y*32)),fill=(0xFF,0,0))
                            #bottom
                            self.draw.line(((x*32,y*32+31),(x*32+31,y*32+31)),fill=(0xFF,0,0))
                            #left
                            self.draw.line(((x*32,y*32),(x*32, y*32+31)),fill=(0xFF,0,0))
                            #right
                            self.draw.line(((x*32+31,y*32),(x*32+31, y*32+31)),fill=(0xFF,0,0))
                    if self.debug["water"]:
                        if tile["flags"] & 4:
                            #top
                            self.draw.line(((x*32+1,y*32+1),(x*32+30,y*32+1)),fill=(0,0,0xFF))
                            #bottom
                            self.draw.line(((x*32+1,y*32+30),(x*32+30,y*32+30)),fill=(0,0,0xFF))
                            #left
                            self.draw.line(((x*32+1,y*32+1),(x*32+1, y*32+30)),fill=(0,0,0xFF))
                            #right
                            self.draw.line(((x*32+30,y*32+1),(x*32+30, y*32+30)),fill=(0,0,0xFF))
                    if self.debug["blight"]:
                        if tile["flags"] & 2:
                            #top
                            self.draw.line(((x*32+2, y*32+2),(x*32+29,y*32+2)), fill=(0xFF,0,0xFF))
                            #bottom
                            self.draw.line(((x*32+2,y*32+29),(x*32+29,y*32+29)),fill=(0xFF,0,0xFF))
                            #left
                            self.draw.line(((x*32+2,y*32+2),(x*32+2,y*32+29)),  fill=(0xFF,0,0xFF))
                            #right
                            self.draw.line(((x*32+29,y*32+2),(x*32+29,y*32+29)),fill=(0xFF,0,0xFF))
                        
if __name__ == "__main__":
    from read_w3e import ReadW3E
    settings = {
        "invalidTile" : True,
        "validTile" : False,
        "ramp" : True,
        "height" : True,
        "water" : True,
        "blight" : True
    }
    image = TopDownViewer(ReadW3E("input/war3map.w3e"), settings)
    image.img.save("ui/tmp/test.png", "PNG")
