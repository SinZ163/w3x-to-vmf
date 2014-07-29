from mpyq import MPQArchive

from lib.DataReader import DataReader

## Modified MPQ Reader for WC3 map files
class WC3Map_MPQ(MPQArchive):
    def __init__(self, filehandler, listfile=True, strict = True, forceV1 = False):
        self.file = filehandler
        self.strict = strict
        self.forceV1 = forceV1
            
        self.header = self.read_header()
        #print(self.header)
        
        self.hash_table = self.read_table('hash')
        #print(self.hash_table)
        
        self.block_table = self.read_table('block')
        
        if listfile:
            self.files = self.read_file('(listfile)').splitlines()
        else:
            self.files = None
    
    def read_header(self):
        #"""Read the header of a MPQ archive."""
        ## Read the header of a WC3 MPQ archive
        
        magic = self.file.read(4)
        self.file.seek(0)
        
        #print(magic)
        
        if magic == "HM3W":
            datReader = DataReader(self.file)
            header = {}
            ## should be HM3W
            header["wc3map_magic"] = datReader.charArray(4)
            
            ## unknown
            datReader.int()
            header["wc3map_mapName"] = datReader.string()
            print(header["wc3map_mapName"])
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
            header["wc3map_mapFlags"] = datReader.flags()
            header["wc3map_maxPlayers"] = datReader.int()
            self.file.seek(512)
        else:
            ## If the magic isn't HM3W, we will skip the first 512 bytes of the 
            ## file anyway 
            self.file.seek(512)
            
        print(self.file.tell())
        magic = self.file.read(4)
        self.file.seek(512)
        print( len(magic))
        print(magic, hex(ord(magic[3])) )
        
        if magic == b'MPQ\x1a' or self.forceV1 == True:
            i = 1
            
            while magic != "MPQ\x1a":
                i += 1
                self.file.seek(512*i)
                magic = self.file.read(4)
            
            self.file.seek(512*i)
            header.update(self.__read_mpq_header__())
            header['offset'] = 512*i
        elif magic == b'MPQ\x1b':
            user_data_header = self.__read_mpq_user_data_header__()
            header.update(self.__read_mpq_header__(user_data_header['mpq_header_offset']))
            header['offset'] = user_data_header['mpq_header_offset']
            header['user_data_header'] = user_data_header
            
        else:
            raise ValueError("Invalid file header.")

        return header
    
    def extract_files(self, filenames, folder = ""):
        """Extract given files from the archive to disk."""
        ## Modification: Can extract files to a folder
        if folder != "":
            path = os.path.join(folder, "")
        else:
            path = ""
            
        for filename in filenames:
            data = self.read_file(filename)
            f = open(path+filename, 'wb')
            f.write(data or "")
            f.close()