import os
import traceback
import simplejson
from cStringIO import StringIO

from lib.mpyq.wc3_mpyq import WC3Map_MPQ
from lib.mpyq.mpyq_compression import UnsupportedCompressionAlgorithm

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
    def __init__(self, filehandle, useListfile = False, strict = True, forceV1 = False):
        self.mpq = WC3Map_MPQ(filehandle, useListfile, strict, forceV1)
        self.listfile = {}
        #self.createListfile()
    
    # The createListfile method uses an external list of filenames
    # for checking which files exist in the given wc3 map.
    # Per default it uses the wc3Files.txt file,
    # but a custom list can be supplied with the template argument.
    def createListfile(self, template = None):
        
        if template == None:
            standard_list = open(os.path.join("lib", "wc3Files.txt"), "r")
        else:
            standard_list = template
        
        for filename in standard_list:
            filename = filename.rstrip()
            exists = self.mpq.file_exists(filename)
            
            if exists == True:
                print filename, "found"
                self.listfile[filename] = True
    
    # Attempt to read all files listed in the listfile variable
    # and put out any exception that appears.
    def debug_tryAllFiles(self):
        for filename in self.listfile:
            try:
                file = self.mpq.read_file(filename)
                print filename, "is fine"
            except UnsupportedCompressionAlgorithm as error:
                print filename, "has unsupported compression: ",error.name, error.used_algorithms, hex(error.compression_type)
            except Exception as error:
                print filename, "caused an exception:", str(error)
                traceback.print_exc()
    
    def read_file(self, filename):
        file = self.mpq.read_file(filename)
        if file != None:
            filehdlr = StringIO(file)
            return filehdlr
        else:
            # File has not been found.
            return None
                
                
        

if __name__ == "__main__":
    WCdirectory = "C:\\Games\\Warcraft III\\Maps\\CustomMaps"
    files = os.listdir(WCdirectory)
    
    for filename in files:
        path = os.path.join(WCdirectory, filename)
        if os.path.isdir(path):
            continue
        
        print "\n======================="
        print path
        
        with open(path, "rb") as f:
            mymap = WC3Map(f, strict = True, forceV1 = True)
            mymap.createListfile(template = open("lib/wc3Files_compact.txt"))
            mymap.debug_tryAllFiles()
            
            ## Code for reading a file raw and writing each sector of the file
            ## into seperate files in a debug_stuff/sectors/ directory.
            ## Not recommended when reading more than one map at once.
            #data = mymap.mpq.read_file("war3mapMap.blp", raw = True)
            #for i, sector in enumerate(data):
            #    with open(os.path.join("debug_stuff", 
            #                           "sectors", 
            #                           "sector_"+str(i)+"_"+str(sector[0])), "w") as f:
            #        f.write(sector[1][1:])
            