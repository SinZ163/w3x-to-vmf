import struct
import os

class DataReader():
    def __init__(self, filename):
        if isinstance(filename, basestring):
            self.hdlr = open(filename, "rb") 
            self.maxSize = os.path.getsize(filename) 
            self.index = 0
        else:
            self.hdlr = filename
            
            try:
                self.maxSize = os.path.getsize(self.hdlr.name)
            except Exception as error:
                print type(filename)
                original_pos = self.hdlr.tell()
                
                try:
                    self.hdlr.seek(0, 2)
                except TypeError:
                    #silly BytesIO
                    self.hdlr.seek(0, 2)
                self.maxSize = self.hdlr.tell() 
                
                self.hdlr.seek(original_pos)
                
            self.index = self.hdlr.tell()
        
        self.TriggerDict = {}
        self.use_triggerDict = False
            
        
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
        
        finished = False
        
        stringindex = 0
        startIndex = self.hdlr.tell()
        for i in xrange(self.maxSize-self.index):
            byte = self.hdlr.read(1)
            stringindex += 1
            if ord(byte) != 0:
                pass
                #utfarray.append(byte)
            else:
                finished = True
                break
            
        
        if finished == False:
            raise RuntimeError("Tried to read string and reached end of file! String started at i={0}".format(self.index))
        else:    
            self.index += stringindex
            self.hdlr.seek(startIndex)
            
            string = self.hdlr.read(stringindex)[0:-1]
            utfstring = string.decode("utf-8", errors="replace")
            
            if self.use_triggerDict == True:
                translated_string = self.translate_trigger(utfstring)
                if translated_string != None:
                    return translated_string
            
            
            
            return utfstring
        
        
    def flags(self):
        #Flags are booleans stored in 4 bytes
        # Flags are read starting with the least significant byte first
        
        int = self.int()
        flags = []
        
        for i in xrange(4*8):
            flag = (int >> i) & 1
            
            flags.append(flag)
        
        return flags
    
    def load_triggerDB(self, triggerDB):
        self.TriggerDict = triggerDB
        self.use_triggerDict = True
    
    def translate_trigger(self, string):
        keyword, sep, number = string.partition("_")
        if string.count("TRIGSTR") > 1:
            print ("WARNING: STRING HAS MORE THAN ONE OCCURENCE OF TRIGSTR\n"
                   "Please report the file to the authors of wc3-to-vmf "
                   "for further investigation. Thank you.")
        
        # 0's at the start are ignored.
        number = number.lstrip("0")
            
        if keyword != "TRIGSTR":
            # Not a trigger string.
            return None
        elif len(number) == 0:
            # TRIGSTR_ refers to the trigger string number 0.
            triggerID = 0
        elif number[0] == "-":
            # Number is negative and does not refer to
            # any string. According to http://www.wc3c.net/tools/specs/
            # it is displayed as "".
            return ""
        elif not number[0].isdigit():
            # Number is not a digit, that means it is a reference to
            # the trigger string number 0, according to http://www.wc3c.net/tools/specs/
            triggerID = 0
        else:
            for i, char in enumerate(number):
                if not char.isdigit:
                    # Omit the last non-digit character and return 
                    # the number string as an integer.
                    triggerID = int(number[0:i-1])
            else:
                triggerID = int(number)
        
        if triggerID in self.TriggerDict:
            return "\n".join(self.TriggerDict[triggerID])
        else:
            raise RuntimeError("Trigger ID doesn't exist: {0}".format(triggerID))
                
        
            
    