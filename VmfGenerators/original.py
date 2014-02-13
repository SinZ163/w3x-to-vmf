


class VmfGen():
    def __init__(self, base):
        self.base = base
        self.name = "Brush VMF"
        self.description = "Brush-based VMF creation using a simple algorithm to reduce the amount of brushes used."
        
        print "{0} initialized".format(self.name)
    
    def create_vmf(self):
        pass
    
    def rectangularCheck(startX, startY, neededHeight):
        do_break = False
        
        x_limit = base.data.mapInfo["width"]
        y_limit = base.data.mapInfo["height"]
        
        for x in xrange(startX, x_limit):
            for y in xrange(startY, y_limit):
                if base.heightmap.getVal(x, y) == neededHeight and blobAffinity.getVal(x, y) == -1:
                    pass
                else:
                    # Damnit Python, why is there no built-in way to break out
                    # of multiple loops? :(
                    if x > startX:
                        do_break = True
                    else:
                        y_limit = y
                    break
                
            if do_break == True:
                x_limit = x
                break
                    
        return (x_limit, y_limit)