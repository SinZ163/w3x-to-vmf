import os
import traceback
import simplejson

from lib.mpyq import WC3Map_MPQ, UnsupportedCompressionAlgorithm

from lib.ReadFiletype.read_doo import read_doodad
from lib.ReadFiletype.read_slk import read_SLK
from lib.ReadFiletype.read_w3e import read_W3E
from lib.ReadFiletype.read_w3i import read_W3I
from lib.ReadFiletype.read_wpm import read_WPM
from lib.ReadFiletype.read_wts import read_WTS
from lib.ReadFiletype.read_object import read_object
 

# This object will provide an interface for accessing the 
# various data of a wc3 map. It will unpack the MPQ data from
# the map, and it will automatically use the read_<insert file format>
# scripts to extract the information from the files.
class WC3Map():
    def __init__(self, filehandle, useListfile = False, strict = False, forceV1 = False):
        self.mpq = WC3Map_MPQ(filehandle, useListfile, strict, forceV1)
        self.listfile = []
        
    def createListfile(self):
        standard_list = open(os.path.join("lib", "wc3Files.txt"), "r")
        
        for line in standard_list:
            line = line.rstrip()
            
            try:
                file = self.mpq.read_file(line)
            except UnsupportedCompressionAlgorithm as error:
                print line, "has unsupported compression: ",error.name, error.used_algorithms
                self.listfile.append(file)
            except Exception as error:
                print line, "caused an exception:", str(error)
                traceback.print_exc()
            else:
                if file != None:
                    print line, "found"
                    self.listfile.append(file)
        

if __name__ == "__main__":
    WCdirectory = "C:\\Games\\Warcraft III\\Maps\\CustomMaps"
    files = os.listdir(WCdirectory)

    for filename in  files:
        path = os.path.join(WCdirectory, filename)
        if os.path.isdir(path):
            continue
        
        print "\n======================="
        print path
        
        with open(path, "rb") as f:
            try:
                mymap = WC3Map(f, forceV1 = True)
                mymap.createListfile()
            except OverflowError:
                print path, "CAUSES OVERFLOWERROR"
                traceback.print_exc()