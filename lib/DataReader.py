import struct
import os

class DataReader():
    def __init__(self, filename):
        if isinstance(filename, str):
            self.hdlr = open(filename, "rb") 
            self.maxSize = os.path.getsize(filename) 
            self.index = 0
        else:
            self.hdlr = filename
            self.maxSize = os.path.getsize(self.hdlr.name)
            self.index = self.hdlr.tell()
            
        
    def int(self):
        #Integer is 4 bytes, little endian
        self.index += 4
        data = self.hdlr.read(4)
        return struct.unpack("<i", data)[0]
    def short(self):
        #Short is 2 bytes, little endian
        self.index += 2
        data = self.hdlr.read(2)
        return struct.unpack("<h", data)[0]
    
    def float(self):
        #Float is 4 byte little endian
        self.index += 4
        data = self.hdlr.read(4)
        return struct.unpack("<f", data)[0]
    
    def char(self):
        #1 char = 1 byte
        self.index += 1
        data = self.hdlr.read(1)
        info = struct.unpack("c", data)[0]
        return info
    
    def charArray(self, len):
        info = []
        for i in range(0,len):
            info.append(self.char())
        return "".join(info)
    
    def byte(self):
        #Not in the specifications, but is a byte..
        self.index += 1
        data = self.hdlr.read(1)
        return struct.unpack("B", data)[0]
    
    def byteArray(self, len):
        self.index += len
        data = self.hdlr.read(len)
        bytes = struct.unpack(str(len)+"B", data)
        return bytes
    
    def nibbles(self):
        #Not in the specifications, but is a 4bit entry
        self.index += 1
        data = self.hdlr.read(1)
        byte = struct.unpack("B", data)[0]
        
        nibble1, nibble2 = (byte & 0xF0) >> 4, byte & 0x0F
        return nibble1, nibble2
    
    def string(self):
        #is UTF-8
        #Read until \0 (null character)
        #If prefixed with "TRIGSTR_", it is to reference a string from memory
        
        utfarray = []
        finished = False
        stringindex = 0
        for i in xrange(self.maxSize-self.index):
            stringindex += 1
            byte = self.hdlr.read(1)
            if ord(byte) != 0:
                utfarray.append(byte)
            else:
                finished = True
                break
        
        if finished == False:
            raise RuntimeError("Tried to read string and reached end of file! String started at i={0}".format(self.index))
        else:    
            self.index += stringindex
            utfstring = "".join(utfarray)
            
            return utfstring
        
        
        
    def flags(self): #not used in w3e, ignoring <- disregard that, no reason not to add it <3
        #Flags are booleans stored in 4 bytes
        
        # Flags are read starting with the least significant byte first
        
        int = self.int()
        flags = []
        
        for i in range(4*8):
            flag = int & (1 << i)
            
            flags.append(flag)
        
        return flags