class ReadDoodad:
    def __init__(self, filename):
        self.read = DataReader(filename)
        self.info = self.ReadDoodad()
        
    def ReadDoodad(self):
        doodInfo = self.ReadHeader()
        doodInfo["trees"] = []
        for i in xrange(0, doodInfo["count"]):
            doodInfo["trees"].append(self.ReadTreeData())
        doodInfo["special"] = self.ReadSpecialDoodads()
        
    def ReadHeader(self):
        return {
            "fileID" : read.charArray(4),
            "version" : read.int(),
            "subVersion" : read.int(),
            "count" : read.int()
        }
    def ReadTreeData(self):
        treeInfo = {
            "treeID" : read.charArray(4),
            "variation" : read.int(),
            "coord" : {
                "x" : read.float(),
                "y" : read.float(),
                "z" : read.float()
            },
            "angle" : read.float(),
            "scale" : {
                "x" : read.float(),
                "y" : read.float(),
                "z" : read.float()
            },
            "flags" : read.byte(),
            "life" : read.byte(),
            "itemPoint" : read.int()
        }
        if treeInfo["itemPoint"] >= 0:
            raise RuntimeError("What is items")
            
        treeInfo["doodID"] = read.int()
        return treeInfo
        
    def ReadSpecialDoodads(self):
        specialInfo = {}
        specialInfo["version"] = read.int()
        specialInfo["count"] = read.int()
        specialInfo["info"] = []
        for i in xrange(0,count)
            specialInfo["info"].append({
                "ID" : read.charArray(4),
                "z" : read.int(),
                "x" : read.int(),
                "y" : read.int()
            })
        return specialInfo
"""        
for i in xrange(0,count):
    treeID = read.charArray(4)
    variation = read.int()
    xCoord = read.float()
    yCoord = read.float()
    zCoord = read.float()
    angle = read.float() #in radians
    xScale = read.float()
    yScale = read.float()
    zScale = read.float()
    flags = read.byte()
    life = read.byte() #in percentage
    itemPointer = read.int()
    if itemPointer == -1:
        #no item table
        pass
    elif itemPointer >=0:
        itemCount = read.int()
        for j in xrange(0,itemCount):
            count = read.int() #really?
            itemID = read.charArray(4)
            itemChoice = read.int()
"""