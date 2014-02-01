#import Image
#import ImageFont
#import ImageDraw
from PIL import Image, ImageFont, ImageDraw

from read_w3e import ReadW3E
class TopDownViewer:
                    
    def __init__(self, mapInfo):
        self.textures = self.Texture("ui/WC3 Art/ground",
                   {"Ashen_Leaves.tga" : "Alvd",
                    "City_DirtRough.tga" : "Ydtr",
                    "Ice_Dirt.tga" : "Idrt",
                    "Ice_DarkIce.tga" : "Idki",
                    "Ice_DirtRough.tga" : "Idtr",
                    "Ice_Ice.tga" : "Iice",
                    "Ice_RuneBricks.tga" : "Irbk",
                    "Ice_Snow.tga" : "Isnw"})
        self.placeholder = Image.open("ui/WC3 Art/placeholder.tga")
        
        self.font = ImageFont.truetype("arial.ttf", 15)
        self.data = mapInfo
        self.img = Image.new("RGB", (self.data.mapInfo["width"]*32, self.data.mapInfo["height"]*32))

        self.draw = ImageDraw.Draw(self.img)
        self.work()
    def Texture(self, folder, textDict):
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
                
                
                tiletype = tile["nibble1"] & 0xF
                type = self.data.mapInfo["groundTileSets"][tiletype]
                
                y = self.data.mapInfo["height"] - y-1
                
                if type in self.textures["dict"]:
                    #subindex = tile["textureDetails"]
                    subindex = 0
                    
                    try:
                        self.img.paste(self.textures["dict"][type][subindex], (x*32, y*32))#
                        #bla = str(bin(subindex))[2:]
                        #print bla.zfill(8)
                        self.draw.text((x*32+1, y*32), str(hex(subindex)), font = self.font, fill = (0, 255, 33))
                        self.draw.text((x*32+1, y*32+15), str(type), font = self.font, fill = (140, 140, 140, 200))
                    except:
                        #pass
                        self.img.paste(self.placeholder, (x*32, y*32))
                        self.draw.text((x*32+1, y*32), str(hex(subindex)), font = self.font, fill = (255, 0, 33))
                        self.draw.text((x*32+1, y*32+15), str(type), font = self.font, fill = (140, 140, 140, 200))
                    #is it a ramp
                    flags = tile["nibble1"] >> 4
                    #print(flags)
                    #print("Ramp: "+str(flags & 1))
                    if flags & 1:
                        #top
                        self.draw.line(((x*32,y*32),(x*32+31,y*32)),fill=(0xFF,0,0))
                        #bottom
                        self.draw.line(((x*32,y*32+31),(x*32+31,y*32+31)),fill=(0xFF,0,0))
                        #left
                        self.draw.line(((x*32,y*32),(x*32, y*32+31)),fill=(0xFF,0,0))
                        #right
                        self.draw.line(((x*32+31,y*32),(x*32+31, y*32+31)),fill=(0xFF,0,0))
image = TopDownViewer(ReadW3E("input/war3map.w3e"))
image.img.save("ui/tmp/test.png", "PNG")
