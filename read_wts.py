#The triggers database
import simplejson
import os
class ReadWTS:
    currentString = None
    readData = None
    def __init__(self, filename):
        self.filename = filename
        self.triggers = {}
        self.readLoop()
    def readLoop(self):
        status = 0
        with open(self.filename) as f:
            for line in f:
                lineSplit = line.split()
                if self.currentString:
                    if "{" in lineSplit[0]:
                        self.triggers[self.currentString] = []
                        continue
                    elif "}" in lineSplit[0]:
                        self.currentString = None
                        self.readData = None
                        continue
                    else:
                        lineSplit = line.split()
                        newLine = ""
                        for word in lineSplit:
                            if word == "//":
                                break
                            else:
                                newLine = newLine + word
                        if newLine != "":
                            self.triggers[self.currentString].append(newLine)
                else:              
                    if len(lineSplit) > 0:
                        if "STRING" in lineSplit[0]:
                            self.currentString = lineSplit[1]
if __name__ == "__main__":
    filename = "input/war3map_troll.wts"
    info = ReadWTS(filename)
    try:
        os.makedirs('./output')
    except OSError:
        pass
    with open("output/triggers.json", "w") as f:
        f.write(simplejson.dumps(info.triggers, sort_keys=True, indent=4 * ' '))