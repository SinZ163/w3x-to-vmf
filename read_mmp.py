#menu minimap
from lib.DataReader import DataReader
class MenuMinimap:
    def __init__(self, filename):
        self.read = DataReader(filename)
        self.info = []
        self.__work__()
    def __work__(self):
        unknown = self.read.int()
        count = self.read.int()
        for i in xrange(0,count):
            info = {}
            info["type"] = self.read.int()
            '''
            0: goldmine
            1: house
            2: player start (cross)
            '''
            info["x"] = self.read.int()
            info["y"] = self.read.int()
            info["blue"] = self.read.byte()
            info["green"] = self.read.byte()
            info["red"] = self.read.byte()
            info["alpha"] = self.read.byte()
            self.info.append(info)
if __name__ == "__main__":
    import os
    import simplejson
    filename = "input/war3map.mmp"
    minimapInfo = MenuMinimap(filename)
    try:
        os.makedirs('./output')
    except OSError:
        pass
    with open("output/minimap.json", "w") as f:
        f.write(simplejson.dumps(minimapInfo.info, sort_keys=True, indent=4 * ' '))