#import struct

from lib.DataReader import DataReader
from lib.mpyq import MPQArchive, WC3Map_MPQ

"""
class WC3Reader():
    def __init__(self,filename):
        self.read = DataReader(filename)
        #self.header = self.readHeader()
        self.archive = WC3Map_MPQ(self.read.hdlr, listfile=True)
        try:
            if self.read.index < self.read.maxSize:
                self.footer = self.readFooter()
        except:
            print("No footer found.")
    
    #    W3M/W3X footer is optional, and only useful for offical W3M maps
    
    def readFooter(self):
        footerInfo = {}
        #should be NGIS, "SIGN" backwards
        footerInfo["signID"] = self.read.charArray(4)
        #unknown usage
        footerInfo["bytes"] = self.read.byteArray(256)
        return footerInfo"""


# Generating a basic listfile for the map. Basically, we iterate over the 
# listfile template and check if we can read each file from the archive. 
# Depending on the output of the read_file function and whether or not an
# exception is raised, we add the file together with a flag to a list.
def generate_listfile(wc3files, mpq):
    filelist = open(wc3files, "r")
    
    listfile = []
    
    for line in filelist:
        #try:
        output = mpq.read_file(line.strip())
        
        if output != None:
            # The file appears to have been found successful
            listfile.append((line.strip(), True)) 
        else:
            # The file doesn't appear to exist, or has a zero size in the archive
            listfile.append((line.strip(), None)) 
                
        #except Exception as error:
        #    # The file does exist, but there has been some trouble, 
        #    # e.g. the file is encrypted or uses an unsupported compression algorithm
        #    listfile.append((line.strip(), False))
        #    print line.strip(), error
        #                                            
    return listfile

filename = "map.w3x"

archive = WC3Map_MPQ(filename, listfile=False)

print "Trying to generate a listfile"

listfile = generate_listfile("lib/wc3Files.txt", archive)

# We create an empty file
listfile_file = open("output/listfile.txt", "w")
listfile_file.write("")
listfile_file.close()

listfile_file = open("output/listfile.txt", "a")

for entry in listfile:
    if entry[1] in [True, False]:
        listfile_file.write(entry[0]+"\n")

# Done! Please note that this is not always the full listfile.
# Custom maps are likely to have their own listfiles which are located
# in the archive. Sometimes the listfile (and other files) is encrypted,
# but there is no decryption yet.
listfile_file.close()
    
