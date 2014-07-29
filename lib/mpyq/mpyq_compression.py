import zlib
import bz2

class UnsupportedCompressionAlgorithm(Exception):
    def __init__(self, algorithmName, compression_type):
        self.name = algorithmName
        self.used_algorithms = []
        self.compression_type = compression_type
        for algorithm in ( ("IMA ADPCM STEREO",  0b10000000),
                           ("IMA ADPCM MONO",    0b01000000),
                           ("bzip",              0b00010000),
                           ("Imploded",          0b00001000),
                           ("zlib",              0b00000010),
                           ("Huffman",           0b00000001)):
            name, flag = algorithm
            if (compression_type & flag) != 0:
                self.used_algorithms.append(name)
            
        
    def __str__(self):
        return (
                "The algorithm is not yet supported: {0}\n"
                "A complete list of algorithms used in this sector: "
                "{1}".format(self.name, ", ".join(self.used_algorithm) ) 
                )

def decompress(data, strict = True):
    """Read the compression type and decompress file data."""
    compression_type = ord(data[0:1])
    data = data[1:]
    
    ## Compression type is actually a mask that contains data about which
    ## compression algorithms are used. A sector can be compressed using
    ## several compression algorithms.
    otherTypes = 0x10 | 0x8 | 0x2 | 0x1 | 0x80 | 0x40
    #print(bin(compression_type), bin(otherTypes))
    
    ## A little check to give the program more room for exceptions.
    ## Can be useful for debugging, might be removed later.
    ## Flags: 
    ## IMA ADPCM stereo:  0b10000000 
    ## IMA ADPCM mono:    0b01000000
    ## Unused:            0b00100000
    ## bzip:              0b00010000 
    ## Imploded:          0b00001000 
    ## Unused:            0b00000100
    ## zlib:              0b00000010 
    ## Huffman:           0b00000001 
    ## If any of those bits are set, something is not entirely correct
    
    if strict and compression_type & ~otherTypes != 0:
        raise RuntimeError("Compression Type has flags set which should not be set: {0},"
                           "can only handle the following flags: {1}".format(bin(compression_type), bin(otherTypes)))
    
    if compression_type & 0x10: 
        #print("Bz2 decompression...")
        data = bz2.decompress(data)
    
    ## The Implode check might not belong here. According to documentation,
    ## compressed data cannot be imploded, and vice versa.
    if compression_type & 0x8: # 0b00001000
        raise UnsupportedCompressionAlgorithm("Implode", compression_type)
    
    if compression_type & 0x2:
        #print("zlib decompression...")
        try:
            data = zlib.decompress(data, 15)
        except zlib.error:
            ## Sometimes, the regular zlib decompress method fails due to invalid
            ## or truncated data. When that happens, it is very likely that decompressobj
            ## is able to decompress the data.
            #print("Regular zlib decompress method failed. Using decompressObj.")
            
            zlib_decompressObj = zlib.decompressobj()
            data = zlib_decompressObj.decompress(data)
    
    if compression_type & 0x1:
        raise UnsupportedCompressionAlgorithm("Huffman", compression_type)
    
    if compression_type & 0x80:
        raise UnsupportedCompressionAlgorithm("IMA ADPCM stereo", compression_type)
    
    if compression_type & 0x40:
        raise UnsupportedCompressionAlgorithm("IMA ADPCM mono", compression_type)
    
    return data
