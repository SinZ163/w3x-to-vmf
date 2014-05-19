class ReadSLK:
    def __init__(self, filename):
        self.filename = filename
        self.readLoop()
        
    def readLoop(self):
        db = {}
        curX = 0
        curY = 0
        with open(self.filename) as f:
            for lineNumber, line in enumerate(f): 
                if line[0:1] == "C":
                    #Ok, this is a C record
                    value = ""
                    lineInfo = line.split(";")
                    for info in lineInfo:
                        if info == "C":
                            continue
                        if info[0:1] == "Y":
                            #this is changing curY ^.^
                            curY = info[1:]
                        elif info[0:1] == "X":
                            #this is changing curX ^.^
                            curX = info[1:]
                        elif info[0:1] == "K":
                            #this is the actual value of the cell
                            #we also need to dodge the "" as that is annoying
                            if info[2:3] == "\"":
                                print("orig| "+info)
                                print("new | "+info[2:-2])
                                value = info[2:-1]
                            else:
                                value = info[1:]
                    if curY in db:
                        db[curY][curX] = value
                    else:
                        db[curY] = {curX : value}
        self.db = db
def integerSort(key):
    return int(key[0])
    
if __name__ == "__main__":
    import simplejson
    import os
    #This is to test the program, kinda neat
    slkParser = ReadSLK("output/mapdata/Splats_LightningData.slk")
    
    try:
        os.makedirs('./output')
    except OSError:
        pass
    
    with open("output/slk.json", "w") as f:
        f.write(simplejson.dumps(slkParser.db, item_sort_key=integerSort, indent=4 * ' '))
        
    for y, row in sorted(slkParser.db.iteritems()):
        #this is a row
        rowVals = []
        for x in sorted(row):
            rowVals.append(row[x].strip())
        print(" | ".join(rowVals))
        print("----------------------------")