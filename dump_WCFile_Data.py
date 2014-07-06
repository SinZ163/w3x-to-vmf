import os
import traceback
import errno
import simplejson
from optparse import OptionParser

from lib.ReadFiletype.read_doo import read_doodad
from lib.ReadFiletype.read_w3e import read_W3E
from lib.ReadFiletype.read_w3i import read_W3I
from lib.ReadFiletype.read_wpm import read_WPM
from lib.ReadFiletype.read_wts import read_WTS
from lib.ReadFiletype.read_mmp import read_MenuMinimap
from lib.ReadFiletype.read_object import (read_W3U, read_W3T, read_W3B,
                                          read_W3D, read_W3A, read_W3H,
                                          read_W3Q, translate_info) 


OUTPUT = "output/"

READFUNCTIONS = {
                 "doo" : read_doodad, "w3e" : read_W3E,
                 "w3i" : read_W3I, "wpm" : read_WPM,
                 "wts" : read_WTS, "mmp" : read_MenuMinimap,
                 "w3u" : read_W3U, "w3t" : read_W3T,
                 "w3b" : read_W3B, "w3d" : read_W3D,
                 "w3a" : read_W3A, "w3h" : read_W3H,
                 "w3q" : read_W3Q
                 }
TEXTFORMATS = ("wts")
TRANSLATE_SUPPORTED = ("w3u", "w3t", "w3a")
SUPPORTED_FILETYPES = READFUNCTIONS.keys()


usage = "%prog [options] filename"
parser = OptionParser(usage = usage)

parser.add_option("-t", "--type", dest="filetype",
                  help="specify the type of the file in case it has no or an incorrect extension", metavar="FILETYPE")
parser.add_option("-o", "--output",
                  dest="output_filename", default = None,
                  help="name of the output file")
parser.add_option("-d", "--dir",
                  dest="output_directory", default = "output",
                  help="name of the output directory")

parser.add_option("--translate",
                  dest="translate_data",
                  action="store_true",
                  help=("Translate data into a more readable format. "
                        "Only supported for {0}.".format(", ".join(TRANSLATE_SUPPORTED))
                        )
                  )

(options, args) = parser.parse_args()

if len(args) != 1:
    parser.error("wrong number of arguments")

input_file = args[0]
provided_extension = options.filetype
file_extension = input_file.rpartition(".")

if ((provided_extension == None) 
    and (file_extension[1] != ".")):
    parser.error("Unknown filetype, specify a filetype using the --type argument.")
elif provided_extension == None:
    fileType = file_extension[2].lower()
else:
    fileType = provided_extension.lower()

if fileType not in SUPPORTED_FILETYPES:
    parser.error("Unsupported filetype, filetype needs to be one of the following: "
                 "{0}".format(", ".join(SUPPORTED_FILETYPES)))


readMode = fileType in TEXTFORMATS and "r" or "rb"

try:
    with open(input_file, readMode) as f:
        data = READFUNCTIONS[fileType](f)
    
    if options.output_filename == None:
        filenameTuple = os.path.split(input_file)
        inputPath, inputFilename = filenameTuple #
        outFilename = inputFilename+".json"
    else:
        outFilename = options.output_filename
    
    outputDir = options.output_directory
    outputPath = os.path.join(outputDir, outFilename)
    
    if options.translate_data == True:
        if fileType not in TRANSLATE_SUPPORTED:
            raise RuntimeError("No translation supported for file type {0}".format(fileType))
        
        customData = translate_info(data["customInfo"], fileType)
        origData = translate_info(data["originalInfo"], fileType)
        
        data = {"fileVersion" : data["fileVersion"],
                "originalData" : origData,
                "customData" : customData}
        
    with open(outputPath, "w") as f:
        simplejson.dump(data, f, indent=4 * ' ')
        print "Json data saved in {0}".format(outputPath)
    
except IOError as error:
    traceback.print_exc()
except Exception as error:
    print "=================="
    traceback.print_exc()
    print "=================="
    print "An exception occured! Please report the exception."