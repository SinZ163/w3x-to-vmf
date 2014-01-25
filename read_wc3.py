#import struct

from lib.DataReader import DataReader
from lib.mpyq import MPQArchive, WC3Map_MPQ

class WC3Reader():
    def __init__(self,filename):
        self.read = DataReader(filename)
        #self.header = self.readHeader()
        self.archive = WC3Map_MPQ(self.read.hdlr, listfile=False)
        try:
            if self.read.index < self.read.maxSize:
                self.footer = self.readFooter()
        except:
            print("No footer found.")
    """
        W3M/W3X header is *always* 512 bytes, will pad with 0x00's if needed
    """
    def readHeader(self):
        headerInfo = {}
        #should be HM3W
        headerInfo["magic"] = self.read.charArray(4)
        #unknown
        self.read.int()
        headerInfo["mapName"] = self.read.string()
        """
        0x0001: 1=hide minimap in preview screens
        0x0002: 1=modify ally priorities
        0x0004: 1=melee map
        0x0008: 1=playable map size was large and has never been reduced to medium
        0x0010: 1=masked area are partially visible
        0x0020: 1=fixed player setting for custom forces
        0x0040: 1=use custom forces
        0x0080: 1=use custom techtree
        0x0100: 1=use custom abilities
        0x0200: 1=use custom upgrades
        0x0400: 1=map properties menu opened at least once since map creation
        0x0800: 1=show water waves on cliff shores
        0x1000: 1=show water waves on rolling shores
        """
        headerInfo["mapFlags"] = self.read.flags()
        headerInfo["maxPlayers"] = self.read.int()
        self.read.hdlr.read(512 - self.read.index)
        
        return headerInfo
    """
        W3M/W3X footer is optional, and only useful for offical W3M maps
    """
    def readFooter(self):
        footerInfo = {}
        #should be NGIS, "SIGN" backwards
        footerInfo["signID"] = self.read.charArray(4)
        #unknown usage
        footerInfo["bytes"] = self.read.byteArray(256)
        return footerInfo

filename = "map.w3x"
fileInfo = WC3Reader(filename)