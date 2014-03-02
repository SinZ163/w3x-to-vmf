#The .wts file contains the triggers database

import simplejson
import os

class ReadWTS:
    def __init__(self, filename):
        self.filename = filename
        self.triggers = {}
        
        self.currentString = None
        
    def readLoop(self):
        status = 0
        
        with open(self.filename) as f:
            for lineNumber, line in enumerate(f):
                
                if self.currentString != None:
                    if line.startswith("{"):
                        self.triggers[self.currentString] = []
                        continue
                    
                    elif line.startswith("}"):
                        self.currentString = None
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
                            self.triggers[self.currentString].append(newLine)
                else:
                    STRINGpos = line.find("STRING")
                    
                    if STRINGpos != -1:
                        line = line[STRINGpos:]
                        lineSplit = line.split()
                        
                        assert lineSplit[0] == "STRING"
                        
                        stringID = lineSplit[1]
                        self.currentString = int(stringID)

def integerSort(key):
    return int(key[0])

                            
if __name__ == "__main__":
    filename = "input/war3map_troll.wts"
    
    info = ReadWTS(filename)
    info.readLoop()
    
    try:
        os.makedirs('./output')
    except OSError:
        pass
    
    with open("output/triggers.json", "w") as f:
        f.write(simplejson.dumps(info.triggers, item_sort_key=integerSort, indent=4 * ' '))
    
    print ".wts reading finished"