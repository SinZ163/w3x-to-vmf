#The .wts file contains the triggers database

import simplejson
import os

#class ReadWTS:
#    def __init__(self, filename):
#        self.filename = filename
#        self.triggers = {}
#        
#        self.currentString = None
#        
#    def readLoop(self):
def read_WTS(filehandle):
    status = 0
    triggers = {}
    currentString = None
    
    for lineNumber, line in enumerate(f):
        
        if currentString != None:
            if line.startswith("{"):
                triggers[currentString] = []
                continue
            
            elif line.startswith("}"):
                currentString = None
                continue
            
            elif "{" in line or "}" in line:
                print "An unhandled case on line {0}, please check it out and report it.".format(lineNumber+1)
                print line
                raise RuntimeError("{ or } found in line, but not at the start.")
            
            else:
                # Two slashes appear to be used for comments, so we will
                # only read a line until we hit a double slash.
                DoubleSlash = line.find("//")
                
                newLine = line[0:DoubleSlash]
                        
                if newLine != "":
                    triggers[currentString].append(newLine)
        else:
            STRINGpos = line.find("STRING")
            
            if STRINGpos != -1:
                line = line[STRINGpos:]
                lineSplit = line.split()
                
                assert lineSplit[0] == "STRING"
                
                stringID = lineSplit[1]
                currentString = int(stringID)
    
    return triggers

def __integerSort__(key):
    return int(key[0])

                            
if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    
    with open(filename, "r") as f:
        triggerinfo = ReadWTS(filename)
    
    try:
        os.makedirs('./output')
    except OSError:
        pass
    
    with open("output/triggers.json", "w") as f:
        f.write(simplejson.dumps(triggerinfo, item_sort_key = __integerSort__, indent=4 * ' '))
    
    print ".wts reading finished"