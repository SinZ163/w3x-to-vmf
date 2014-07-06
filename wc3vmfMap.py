import os
import array
import math
import time

from timeit import default_timer as timer

try:
    from PIL import Image # Uses Pillow to draw a graphic representation of the map
    pillow_installed = True
except:
    pillow_installed = False


import lib.vmflib as vmflib
import lib.vmflib.tools as tools


from lib.ReadFiletype.read_w3e import read_W3E
from lib.dataTypes import QuadBlobs, Bytemap
from lib.helperFunctions import make_number_divisible_by_n, map_list_with_vertex

from VmfGenerators import brushBlocks, displacement

# A class that centralizes a lot of the functions used 
# in writevmf and writevmf_displacementTest.
class WarvmfMap():
    def __init__(self, wc3_filename, vmf_filename, texture="dota2"):
        self.wc3_filename = wc3_filename
        self.vmf_filename = vmf_filename
        
        self.debug_timetaken = {}
        
        self.wc3_tileSize = 64
        self.wc3_tileHeight = 64
        
        self.vmfGenerators = {"brush" : brushBlocks.VmfGen(self, texture),
                              "displacement" : displacement.VmfGen(self, texture)}
        
    def setup(self):
        self.__readWar3map__()
        self.__setup_vmf__()
    
    def __readWar3map__(self):
        start = timer()
        
        with open(self.wc3_filename, "rb") as f:
            self.wc3_mapinfo = read_W3E(f)
            
        self.debug_timetaken["WC3 Map Reading"] = timer()-start
        
        self.WC3map_xSize =  self.wc3_mapinfo["width"]
        self.WC3map_ySize =  self.wc3_mapinfo["height"]
        self.WC3map_zSize = 15 # The maximal layer height for a wc3 map is 15 
        
        self.WC3map_heightmap, self.WC3map_rampmap, maxHeight = self.__war3_setup_bytemaps__()
    
    def __war3_setup_bytemaps__(self):
        heightmap = Bytemap(self.WC3map_xSize, self.WC3map_ySize)
        rampMap = Bytemap(self.WC3map_xSize, self.WC3map_ySize, init = 0, dataType = "B")
        
        # Not sure if the maximal height of a WC3 map is useful,
        # we will keep it in mind.
        maxHeight = 0
        
        for x in xrange(self.WC3map_xSize):
            for y in xrange(self.WC3map_ySize):
                index = y*self.WC3map_xSize + x
                tile =  self.wc3_mapinfo["info"][index]
                
                height = tile["layerHeight"]
                
                ramp_flag = (tile["flags"] & 0x1)
                rampMap.setVal(x, y, ramp_flag)
                
                
                ## voodoo magic, disabled for now until I understand it
                #The tilepoint "final height" you see on the WE is given by:
                #(ground_height - 0x2000 + (layer - 2)*0x0200)/4
                #height = tile["groundHeight"] - 0x2000 + ((tile["nibble2"] & 0xF) -2) *0x0200 / 4
                #if height < lowestHeight:
                #    lowestHeight = height
                
                if height > maxHeight: maxHeight = height
                heightmap.setVal(x, y, height)
        
        return heightmap, rampMap, maxHeight
        
    
    def __setup_vmf__(self):
        self.m = vmflib.vmf.ValveMap()
        
        # The sky name can be changed at any time, it will only take effect when you load
        # the map in hammer. If you did not set up the Source SDK for Dota2, check
        # http://developer.valvesoftware.com/wiki/Sky_List for a list of skyboxes you can
        # use in the source SDK of your choice. 
        self.m.world.skyname = "sky_dotasky_01"
        
        self.tileSize = self.wc3_tileSize
        self.tileHeight = self.wc3_tileHeight
        
        # The resulting vmf map has to be much bigger than the WC3 map.
        self.vmfmap_xSize = self.WC3map_xSize * self.tileSize
        self.vmfmap_ySize = self.WC3map_ySize * self.tileSize
        self.vmfmap_zSize = self.WC3map_zSize * self.tileHeight * 2 # We double the height for more room on the map
        
        # Two constants we will use to keep the middle of the vmf map 
        # at the coordinates 0,0. This allows us to keep the map in the bounds
        # of the source engine's capabilities.
        self.vmfmap_xMidOffset = self.vmfmap_xSize // 2
        self.vmfmap_yMidOffset = self.vmfmap_ySize // 2
        self.vmfmap_zMidOffset = self.vmfmap_zSize // 2
        
        # Now setting up the skybox with 5 brushes.
        orig = vmflib.types.Vertex(0,0-self.vmfmap_yMidOffset, 0+self.vmfmap_zMidOffset)
        skybox_back = tools.Block(origin = orig, dimensions=(self.vmfmap_xSize, 8, self.vmfmap_zSize))
        skybox_back.set_material("tools/toolsskybox")
        
        orig = vmflib.types.Vertex(0,0+self.vmfmap_yMidOffset, 0+self.vmfmap_zMidOffset)
        skybox_front = tools.Block(origin = orig, dimensions=(self.vmfmap_xSize, 8, self.vmfmap_zSize))
        skybox_front.set_material("tools/toolsskybox")
        
        orig = vmflib.types.Vertex(0-self.vmfmap_xMidOffset,0, 0+self.vmfmap_zMidOffset)
        skybox_left = tools.Block(origin = orig, dimensions=(8, self.vmfmap_ySize, self.vmfmap_zSize))
        skybox_left.set_material("tools/toolsskybox")
        
        orig = vmflib.types.Vertex(0+self.vmfmap_xMidOffset, 0, 0+self.vmfmap_zMidOffset)
        skybox_right = tools.Block(origin = orig, dimensions=(8, self.vmfmap_ySize, self.vmfmap_zSize))
        skybox_right.set_material("tools/toolsskybox")
        
        orig = vmflib.types.Vertex(0,0, 0+self.vmfmap_zSize)
        skybox_ceiling = tools.Block(origin = orig, dimensions=(self.vmfmap_xSize, self.vmfmap_ySize, 8))
        skybox_ceiling.set_material("tools/toolsskybox")
        
        
        lowestHeight = 16 # Placeholder value for now

        # We create a floor and mark it with a normal texture
        orig = vmflib.types.Vertex(0, 0, 0-lowestHeight//2)
        floor = tools.Block(origin = orig, dimensions=(self.vmfmap_xSize, self.vmfmap_ySize, lowestHeight))
        floor.set_material("nature/dirtfloor012a")
        
        self.m.world.children.append(skybox_back)
        self.m.world.children.append(skybox_front)
        self.m.world.children.append(skybox_left)
        self.m.world.children.append(skybox_right)
        self.m.world.children.append(skybox_ceiling)
        
        self.m.world.children.append(floor)
    
    def generateVmf(self, method):
        self.vmfGenerators[method].create_vmf()
    
    def saveVmf(self):
        #self.vmfGenerators[method].save_vmf()
        self.m.write_vmf(self.vmf_filename)
        
if __name__ == "__main__":
    import sys
    start = time.time()
    wc3map = WarvmfMap(sys.argv[1], "output/war3map.vmf")
    wc3map.wc3_tileSize = 64
    wc3map.wc3_tileHeight = 64
    
    wc3map.setup()
    
    print "WarvmfMap object initialized in {0} seconds".format(time.time() - start)
    midtime = time.time()
    
    wc3map.generateVmf("brush")
    
    print "VMF generated in {0} seconds".format(time.time() - midtime)
    endtime = time.time()
    
    wc3map.saveVmf()
    
    print "VMF file saved in {0} seconds".format(time.time() - endtime)
        
        
        