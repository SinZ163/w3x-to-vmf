#menu minimap
from lib.DataReader import DataReader


def read_MenuMinimap(filehandle):
    read = DataReader(filehandle)
    menuMinimapInfo = []
    
    unknown = read.int()
    count = read.int()
    
    for i in xrange(0,count):
        info = {}
        info["type"] = read.int()
        '''
        Types:
        0: goldmine
        1: house
        2: player start (cross)
        '''
        
        info["x"] = read.int()
        info["y"] = read.int()
        info["blue"] = read.byte()
        info["green"] = read.byte()
        info["red"] = read.byte()
        info["alpha"] = read.byte()
        
        menuMinimapInfo.append(info)
    
    return menuMinimapInfo

"""
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
        f.write(simplejson.dumps(minimapInfo.info, sort_keys=True, indent=4 * ' '))"""