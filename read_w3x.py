from DataReader import DataReader
class W3XReader():
    def __init__(self,read):
        self.read = read
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
class MPQReader():
    def __init__(self,read):
        self.read = read
    """
    The archive header is the first structure in the archive, at archive offset 0, but the archive does not need to be at offset 0 of the containing file.
    The offset of the archive in the file is referred to here as ArchiveOffset. If the archive is not at the beginning of the file,
    it must begin at a disk sector boundary (512 bytes).
    Early versions of Storm require that the archive be at the end of the containing file (ArchiveOffset + ArchiveSize = file size),
    but this is not required in newer versions (due to the strong digital signature not being considered a part of the archive).
    """
    def readHeader(self):
        headerInfo = {}
        #must be "MPQ"
        headerInfo["magic"] = self.read.charArray(4)
        #should be 32
        headerInfo["headerSize"] = self.read.int() 
        #Size of the whole archive, including the header.
        #Does not include the strong digital signature, if present.
        #This size is used, among other things, for determining the region to hash in computing the digital signature.
        headerInfo["archiveSize"] = self.read.int()
        #unknown
        self.read.short()
        #Power of two exponent specifying the number of 512-byte disk sectors in each logical sector in the archive.
        #The size of each logical sector the archive is 512 * 2^SectorSizeShift. Bugs in the Storm library dicate that this should always be 3
        headerInfo["sectorSizeShift"] = self.read.byte()
        #Offset to the beginning of the tables, relative to the beginning of the archive.
        headerInfo["hashOffset"] = self.read.int()
        headerInfo["blockOffset"] = self.read.int()
        #number of entries in the hash table. Must be a power of two, and must be less than 65536
        headerInfo["hashEntries"] = self.read.int()
        #number of entries in the block table.
        headerInfo["blockEntries"] = self.read.int()
        
        return headerInfo
    """
    The block table contains entries for each region in the archive.
    Regions may be either files, empty space, which may be overwritten by new files (typically this space is from deleted file data), or unused block table entries.
    Empty space entries should have BlockOffset and BlockSize nonzero, and FileSize and Flags zero; unused block table entries should have BlockSize, FileSize, and Flags zero.
    The block table is encrypted, using the hash of "(block table)" as the key.
    """
    def readBlockTable(self):
        blockInfo = {}
        #Offset of the beginning of the block, relative to the beginning of the archive.
        blockInfo["blockOffset"] = self.read.int()
        #Size of the block in the archive.
        blockInfo["blockSize"] = self.read.int()
        #Size of the file data stored in the block. Only valid if the block is a file; otherwise meaningless, and should be 0.
        #If the file is compressed, this is the size of the uncompressed file data.
        blockInfo["fileSize"] = self.read.int()
        #80000000h: Block is a file, and follows the file data format; otherwise, block is free space or unused.
        #If the block is not a file, all other flags should be cleared, and FileSize should be 0.
        #01000000h: File is stored as a single unit, rather than split into sectors.
        #00020000h: The file's encryption key is adjusted by the block offset and file size (explained in detail in the File Data section). File must be encrypted.
        #00010000h: File is encrypted.
        #00000200h: File is compressed. File cannot be imploded.
        #00000100h: File is imploded. File cannot be compressed.
        blockInfo["flags"] = self.read.flags()
        
        return blockInfo
    """
    Instead of storing file names, for quick access MoPaQs use a fixed, power of two-size hash table of files in the archive.
    A file is uniquely identified by its file path, its language, and its platform. The home entry for a file in the hash table is computed as a hash of the file path.
    In the event of a collision (the home entry is occupied by another file), progressive overflow is used, and the file is placed in the next available hash table entry.
    Searches for a desired file in the hash table proceed from the home entry for the file until either the file is found,
    the entire hash table is searched, or an empty hash table entry (FileBlockIndex of FFFFFFFFh) is encountered.
    The hash table is encrypted using the hash of "(hash table)" as the key.
    """
    def readHashTable(self):
        hashInfo = {}
        #The hash of the file path, using method A.
        hashInfo["filePathHashA"] = self.read.int()
        #The hash of the file path, using method B.
        hashInfo["filePathHashB"] = self.read.int()
        #The language of the file. This is a Windows LANGID data type, and uses the same values.
        #0 indicates the default language (American English), or that the file is language-neutral.
        hashInfo["language"] = self.read.short()
        #The platform the file is used for. 0 indicates the default platform. No other values have been observed.
        hashInfo["platform"] = self.read.byte()
        #If the hash table entry is valid, this is the index into the block table of the file. Otherwise, one of the following two values:
        #FFFFFFFFh: Hash table entry is empty, and has always been empty. Terminates searches for a given file.
        #FFFFFFFEh: Hash table entry is empty, but was valid at some point (in other words, the file was deleted). Does not terminate searches for a given file.
        hashInfo["fileBlockIndex"] = self.read.int()
        
        return hashInfo
filename = "map.w3x"
fileInfo = MPQReader(filename)