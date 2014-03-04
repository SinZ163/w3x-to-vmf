import os

from lib.DataReader import DataReader
from lib.mpyq import MPQArchive, WC3Map_MPQ, UnsupportedCompressionAlgorithm

# Generating a basic listfile for the map. Basically, we iterate over the 
# listfile template and check if we can read each file from the archive. 
# Depending on the output of the read_file function and whether or not an
# exception is raised, we add the file together with a flag to a list.
def generate_listfile(wc3files, mpq):
    filelist = open(wc3files, "r")
    
    listfile = []
    
    for line in filelist:
        try:
            output = mpq.read_file(line.strip(), raw = False)
            
            if output != None:
                # The file appears to have been found successful
                listfile.append((line.strip(), True)) 
                filename = line.strip().replace("\\", "_")
                
                with open("output/mapdata/"+filename, "wb") as temp:
                    temp.write(output)
                
            else:
                # The file doesn't appear to exist, or has a zero size in the archive
                listfile.append((line.strip(), None)) 
                
        except UnsupportedCompressionAlgorithm as error:
            # The file does exist, but uses an unsupported compression algorithm
            listfile.append((line.strip(), False))
            print line.strip(), error
                                                    
    return listfile

filename = "map.w3x"
#filename = "input/trollsnelves.w3x"

archive = WC3Map_MPQ(filename, listfile=False)

print "Trying to generate a listfile"

try:
    os.mkdir("output/mapdata")
except Exception as error:
    print error
    print "Continuing"
    

listfile = generate_listfile("lib/wc3Files.txt", archive)

# We create an empty file
listfile_file = open("output/listfile.txt", "w")
listfile_file.write("")
listfile_file.close()

listfile_file = open("output/listfile.txt", "a")

for entry in listfile:
    if entry[1] == True:
        listfile_file.write(entry[0]+" successfully read\n")
    elif entry[1] == False:
        listfile_file.write(entry[0]+" found, but unsupported compression algorithm\n")

# Done! Please note that this is not always the full listfile.
# Custom maps are likely to have their own listfiles which are located
# in the archive. Sometimes the listfile (and other files) is encrypted,
# but there is no decryption yet.

#and sometimes custom maps dont use it at all, as for most cases, wc3 knows what files there are anyway
listfile_file.close()
    
