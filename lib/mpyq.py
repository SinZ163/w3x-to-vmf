#!/usr/bin/env python
# coding: utf-8

"""
Original Github page for mpyq: http://github.com/eagleflo/mpyq

mpyq is a Python library for reading MPQ (MoPaQ) archives.

LICENSE:
Copyright (c) 2010-2014 Aku Kotkavuo. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.

  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from __future__ import print_function

import bz2
import os
import struct
import zlib
from collections import namedtuple
from io import BytesIO

## Modification by Yoshi2 & SinZ
## Comments prefixed with ## were not made by the original author, 
## but added as part of the modification of this MPQ library
from DataReader import DataReader


__author__ = "Aku Kotkavuo"
__version__ = "0.2.4"


MPQ_FILE_IMPLODE        = 0x00000100
MPQ_FILE_COMPRESS       = 0x00000200
MPQ_FILE_ENCRYPTED      = 0x00010000
MPQ_FILE_FIX_KEY        = 0x00020000
MPQ_FILE_SINGLE_UNIT    = 0x01000000
MPQ_FILE_DELETE_MARKER  = 0x02000000
MPQ_FILE_SECTOR_CRC     = 0x04000000
MPQ_FILE_EXISTS         = 0x80000000

MPQFileHeader = namedtuple('MPQFileHeader',
    '''
    magic
    header_size
    archive_size
    format_version
    sector_size_shift
    hash_table_offset
    block_table_offset
    hash_table_entries
    block_table_entries
    '''
)
MPQFileHeader.struct_format = '<4s2I2H4I'

MPQFileHeaderExt = namedtuple('MPQFileHeaderExt',
    '''
    extended_block_table_offset
    hash_table_offset_high
    block_table_offset_high
    '''
)
MPQFileHeaderExt.struct_format = 'q2h'

MPQUserDataHeader = namedtuple('MPQUserDataHeader',
    '''
    magic
    user_data_size
    mpq_header_offset
    user_data_header_size
    '''
)
MPQUserDataHeader.struct_format = '<4s3I'

MPQHashTableEntry = namedtuple('MPQHashTableEntry',
    '''
    hash_a
    hash_b
    locale
    platform
    block_table_index
    '''
)
MPQHashTableEntry.struct_format = '2I2HI'

MPQBlockTableEntry = namedtuple('MPQBlockTableEntry',
    '''
    offset
    archived_size
    size
    flags
    '''
)
MPQBlockTableEntry.struct_format = '4I'


class MPQArchive(object):

    def __init__(self, filename, listfile=True):
        """Create a MPQArchive object.

        You can skip reading the listfile if you pass listfile=False
        to the constructor. The 'files' attribute will be unavailable
        if you do this.
        """
        if hasattr(filename, 'read'):
            self.file = filename
        else:
            self.file = open(filename, 'rb')
        self.header = self.read_header()
        self.hash_table = self.read_table('hash')
        self.block_table = self.read_table('block')
        if listfile:
            self.files = self.read_file('(listfile)').splitlines()
        else:
            self.files = None

    def read_header(self):
        """Read the header of a MPQ archive."""

        def read_mpq_header(offset=None):
            if offset:
                self.file.seek(offset)
            data = self.file.read(32)
            header = MPQFileHeader._make(
                struct.unpack(MPQFileHeader.struct_format, data))
            header = header._asdict()
            if header['format_version'] == 1:
                data = self.file.read(12)
                extended_header = MPQFileHeaderExt._make(
                    struct.unpack(MPQFileHeaderExt.struct_format, data))
                header.update(extended_header._asdict())
            return header

        def read_mpq_user_data_header():
            data = self.file.read(16)
            header = MPQUserDataHeader._make(
                struct.unpack(MPQUserDataHeader.struct_format, data))
            header = header._asdict()
            header['content'] = self.file.read(header['user_data_header_size'])
            return header

        magic = self.file.read(4)
        self.file.seek(0)

        if magic == b'MPQ\x1a':
            header = read_mpq_header()
            header['offset'] = 0
        elif magic == b'MPQ\x1b':
            user_data_header = read_mpq_user_data_header()
            header = read_mpq_header(user_data_header['mpq_header_offset'])
            header['offset'] = user_data_header['mpq_header_offset']
            header['user_data_header'] = user_data_header
        else:
            raise ValueError("Invalid file header.")

        return header

    def read_table(self, table_type):
        """Read either the hash or block table of a MPQ archive."""

        if table_type == 'hash':
            entry_class = MPQHashTableEntry
        elif table_type == 'block':
            entry_class = MPQBlockTableEntry
        else:
            raise ValueError("Invalid table type.")

        table_offset = self.header['%s_table_offset' % table_type]
        table_entries = self.header['%s_table_entries' % table_type]
        key = self._hash('(%s table)' % table_type, 'TABLE')
        
        self.file.seek(table_offset + self.header['offset'])
        data = self.file.read(table_entries * 16)
        data = self._decrypt(data, key)
        
        

        def unpack_entry(position):
            entry_data = data[position*16:position*16+16]
            return entry_class._make(
                struct.unpack(entry_class.struct_format, entry_data))

        return [unpack_entry(i) for i in range(table_entries)]

    def get_hash_table_entry(self, filename):
        """Get the hash table entry corresponding to a given filename."""
        hash_a = self._hash(filename, 'HASH_A')
        hash_b = self._hash(filename, 'HASH_B')
        for entry in self.hash_table:
            if (entry.hash_a == hash_a and entry.hash_b == hash_b):
                return entry

    def read_file(self, filename, force_decompress=False, raw = False):
        """Read a file from the MPQ archive."""

        def decompress(data):
            """Read the compression type and decompress file data."""
            compression_type = ord(data[0:1])
            data = data[1:]
            
            ## Compression type is actually a mask that contains data about which
            ## compression algorithms are used. A sector can be compressed using
            ## several compression algorithms.
            otherTypes = 0x10 | 0x8 | 0x2 | 0x1 | 0x80 | 0x40
            print(bin(compression_type), bin(otherTypes))
            
            ## A little check to give the program more room for exceptions.
            ## Can be useful for debugging, might be removed later.
            if compression_type & ~otherTypes != 0:
                raise RuntimeError("Unhandled compression types: {0},"
                                   "can only handle the following flags: ".format(bin(compression_type), bin(otherTypes)))
            
            if compression_type & 0x10:
                data = bz2.decompress(data)
            
            ## The Implode check might not belong here. According to documentation,
            ## compressed data cannot be imploded, and vice versa.
            if compression_type & 0x8 != 0:
                raise RuntimeError("Imploded data not supported yet: {0}".format(compression_type))
            
            if compression_type & 0x2:
                data = zlib.decompress(data, 15)
            
            if compression_type & 0x1:
                raise RuntimeError("Huffman algorithm not supported yet: {0}".format(compression_type))
            
            if compression_type & 0x80:
                raise RuntimeError("IMA ADPCM stereo compression not supported yet: {0}".format(compression_type))
            
            if compression_type & 0x40:
                raise RuntimeError("IMA ADPCM mono compression not supported yet: {0}".format(compression_type))
            
            return data
                

        hash_entry = self.get_hash_table_entry(filename)
        if hash_entry is None:
            return None
        block_entry = self.block_table[hash_entry.block_table_index]
        
        print("______")
        print("File {0} HashEntry Offset: {1} BlockEntry Offset: {2}".format(filename, hash_entry, block_entry))
        
        # Read the block.
        if block_entry.flags & MPQ_FILE_EXISTS:
            if block_entry.archived_size == 0:
                return None
            
            offset = block_entry.offset + self.header['offset']
            
            self.file.seek(offset)
            file_data = self.file.read(block_entry.archived_size)
            
            if raw == True:
                return file_data
            
            
            ## Moved sector calculation to the top. It is more useful here.
            # File consist of many sectors. They all need to be
            # decompressed separately and united.
            
            ## Some WC3 maps like to set the sector size_shift_value high, might
            ## be an attempt to confuse MPQ readers. Generally it should be 3, 
            ## hopefully that is always the case 
            ## sector_size = 512 << self.header['sector_size_shift']
            sector_size = 512 << 3
            sectors = block_entry.size // sector_size + 1
            
            ## We calculate a sectorIndex value to be used in the
            ## decryption of the sector data. Basically, it should be the starting index
            ## of this particular sector.
            ## Is this the correct way to calculate it?
            sectorIndex = (offset - self.header['offset']) // (sector_size-1) + 1
            print(sector_size, sectors, sectorIndex, offset, sector_size, self.header['sector_size_shift'])
            #sectorIndex = block_entry.offset & (~sector_size)
            #print(sectorIndex)
            #print(sectorIndex, self.header['sector_size_shift'])
            
            print("{0} Filedata length: {1}".format(filename, len(file_data)))
            
            ## If file is encrypted, create the decryption key as explained 
            ## in the MPQ documentation on http://www.wc3c.net/tools/specs/QuantamMPQFormat.txt
            if block_entry.flags & MPQ_FILE_ENCRYPTED:
                ## The key is created by hashing the name of the file after
                ## removing the path that prefixes the filename. For this,
                ## we search for the position of the right-most backslash.
                backslash = filename.rfind("\\")
                if backslash != -1:
                    basekey = filename[backslash+1:]
                else:
                    basekey = filename
                
                ## A hash can be created using one of the following types.
                ## We should only need the fourth type.
                ##'TABLE_OFFSET': 0
                ##'HASH_A': 1
                ##'HASH_B': 2
                ##'TABLE': 3
                key = self._hash(basekey, "TABLE")
                
                ## If the Fix_Key flag is set, we need to calculate the final key
                ## as '(base key + BlockOffset - ArchiveOffset) XOR FileSize'.
                ## Is the following code correct?
                if block_entry.flags&MPQ_FILE_FIX_KEY:
                    key = (key + offset - self.header['offset']) ^ block_entry.size
                
                print("Key:", key)
            
            print("Implode: {0}, Compress: {1}, Encrypted: {2}, Fix Key: {3}".format((block_entry.flags&MPQ_FILE_IMPLODE) != 0, (block_entry.flags&MPQ_FILE_COMPRESS) != 0, 
                                                                          (block_entry.flags & MPQ_FILE_ENCRYPTED) != 0, (block_entry.flags&MPQ_FILE_FIX_KEY) != 0))
            
            if not block_entry.flags & MPQ_FILE_SINGLE_UNIT:
                
                if block_entry.flags & MPQ_FILE_SECTOR_CRC:
                    crc = True
                    sectors += 1
                else:
                    crc = False
                
                ## If the file is encrypted, the sector offset table is encrypted, too.
                ## We need to decrypt it before being able to use it. Without the positions,
                ## we do not know where each sector of a compressed file starts.
                if block_entry.flags & MPQ_FILE_ENCRYPTED:
                    sectoroffset_table = file_data[0:(sectors+1)*4]
                    sectoroffset_table = self._decrypt(sectoroffset_table, key-1)
                    
                    positions = struct.unpack('<%dI' % (sectors + 1),
                                              sectoroffset_table)
                else:
                    positions = struct.unpack('<%dI' % (sectors + 1),
                                              file_data[:4*(sectors+1)])
                
                result = BytesIO()
                sector_bytes_left = block_entry.size
                
                print(positions)
                for i in range(len(positions) - (2 if crc else 1)):
                    
                    ## Each sector is decrypted using the key + the 0-based index of the sector.
                    ## Is the following code correct?
                    if block_entry.flags & MPQ_FILE_ENCRYPTED:
                        sectorkey = key + sectorIndex + i
                        
                    sector = file_data[positions[i]:positions[i+1]]
                    
                    ## We try to decrypt the sector data
                    if block_entry.flags & MPQ_FILE_ENCRYPTED:
                            sector = self._decrypt(sector, sectorkey)
                            
                    if (block_entry.flags & MPQ_FILE_COMPRESS and
                        (force_decompress or sector_bytes_left > len(sector))):
                        
                        sector = decompress(sector)
                        
                    sector_bytes_left -= len(sector)
                    result.write(sector)
                    
                file_data = result.getvalue()
            else:
                ## A single unit file should only contain a single sector, so we calculate
                ## the key simply as key + sectorIndex
                if block_entry.flags & MPQ_FILE_ENCRYPTED:
                    print("SingleUnit data length:", len(file_data))
                    sectorkey = key + sectorIndex
                    file_data = self._decrypt(file_data, sectorkey)
                    
                # Single unit files only need to be decompressed, but
                # compression only happens when at least one byte is gained.
                if (block_entry.flags & MPQ_FILE_COMPRESS and
                    (force_decompress or block_entry.size > block_entry.archived_size)):
                    file_data = decompress(file_data)

            return file_data

    def extract(self):
        """Extract all the files inside the MPQ archive in memory."""
        if self.files:
            return dict((f, self.read_file(f)) for f in self.files)
        else:
            raise RuntimeError("Can't extract whole archive without listfile.")

    def extract_to_disk(self):
        """Extract all files and write them to disk."""
        archive_name, extension = os.path.splitext(os.path.basename(self.file.name))
        if not os.path.isdir(os.path.join(os.getcwd(), archive_name)):
            os.mkdir(archive_name)
        os.chdir(archive_name)
        for filename, data in self.extract().items():
            f = open(filename, 'wb')
            f.write(data or "")
            f.close()

    def extract_files(self, *filenames):
        """Extract given files from the archive to disk."""
        for filename in filenames:
            data = self.read_file(filename)
            f = open(filename, 'wb')
            f.write(data or "")
            f.close()

    def print_headers(self):
        print("MPQ archive header")
        print("------------------")
        for key, value in self.header.iteritems():
            if key == "user_data_header":
                continue
            print("{0:30} {1!r}".format(key, value))
        if self.header.get('user_data_header'):
            print()
            print("MPQ user data header")
            print("--------------------")
            for key, value in self.header['user_data_header'].iteritems():
                print("{0:30} {1!r}".format(key, value))
        print()

    def print_hash_table(self):
        print("MPQ archive hash table")
        print("----------------------")
        print(" Hash A   Hash B  Locl Plat BlockIdx")
        for entry in self.hash_table:
            print('{0:0>8X} {1:0>8X} {2:0>4X} {3:0>4X} {4:0>8X}'.format(*entry))
        print()

    def print_block_table(self):
        print("MPQ archive block table")
        print("-----------------------")
        print(" Offset  ArchSize RealSize  Flags")
        for entry in self.block_table:
            print('{0:0>8X} {1:>8} {2:>8} {3:>8X}'.format(*entry))
        print()

    def print_files(self):
        if self.files:
            print("Files")
            print("-----")
            width = max(len(name) for name in self.files) + 2
            for filename in self.files:
                hash_entry = self.get_hash_table_entry(filename)
                block_entry = self.block_table[hash_entry.block_table_index]
                print("{0:{width}} {1:>8} bytes".format(filename.decode(),
                                                        block_entry.size,
                                                        width=width))

    def _hash(self, string, hash_type):
        """Hash a string using MPQ's hash function."""
        hash_types = {
            'TABLE_OFFSET': 0,
            'HASH_A': 1,
            'HASH_B': 2,
            'TABLE': 3
        }
        seed1 = 0x7FED7FED
        seed2 = 0xEEEEEEEE

        for ch in string.upper():
            if not isinstance(ch, int): ch = ord(ch)
            value = self.encryption_table[(hash_types[hash_type] << 8) + ch]
            seed1 = (value ^ (seed1 + seed2)) & 0xFFFFFFFF
            seed2 = (ch + seed1 + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF

        return seed1
    
    def _decrypt(self, data, key):
        """Decrypt hash or block table or a sector."""
        seed1 = key
        seed2 = 0xEEEEEEEE
        result = BytesIO()

        for i in range(len(data) // 4):
            seed2 += self.encryption_table[0x400 + (seed1 & 0xFF)]
            seed2 &= 0xFFFFFFFF
            value = struct.unpack("<I", data[i*4:i*4+4])[0]
            value = (value ^ (seed1 + seed2)) & 0xFFFFFFFF

            seed1 = ((~seed1 << 0x15) + 0x11111111) | (seed1 >> 0x0B)
            seed1 &= 0xFFFFFFFF
            seed2 = value + seed2 + (seed2 << 5) + 3 & 0xFFFFFFFF

            result.write(struct.pack("<I", value))

        return result.getvalue()

    def _prepare_encryption_table():
        """Prepare encryption table for MPQ hash function."""
        seed = 0x00100001
        crypt_table = {}

        for i in range(256):
            index = i
            for j in range(5):
                seed = (seed * 125 + 3) % 0x2AAAAB
                temp1 = (seed & 0xFFFF) << 0x10

                seed = (seed * 125 + 3) % 0x2AAAAB
                temp2 = (seed & 0xFFFF)

                crypt_table[index] = (temp1 | temp2)

                index += 0x100

        return crypt_table

    encryption_table = _prepare_encryption_table()


## Modified MPQ Reader for WC3 map files
class WC3Map_MPQ(MPQArchive):
    def __init__(self, filename, listfile=True):
        if hasattr(filename, 'read'):
            self.file = filename
        else:
            self.file = open(filename, 'rb')
            
        self.header = self.read_header()
        print(self.header)
        
        self.hash_table = self.read_table('hash')
        print(self.hash_table)
        
        self.block_table = self.read_table('block')
        
        if listfile:
            self.files = self.read_file('(listfile)').splitlines()
        else:
            self.files = None
    
    def read_header(self):
        """Read the header of a MPQ archive."""

        def read_mpq_header(offset=None):
            if offset:
                self.file.seek(offset)
            data = self.file.read(32)
            header = MPQFileHeader._make(
                struct.unpack(MPQFileHeader.struct_format, data))
            header = header._asdict()
            
            if header['format_version'] == 1:
                
                data = self.file.read(12)
                extended_header = MPQFileHeaderExt._make(
                    struct.unpack(MPQFileHeaderExt.struct_format, data))
                header.update(extended_header._asdict())
            return header

        def read_mpq_user_data_header():
            data = self.file.read(16)
            header = MPQUserDataHeader._make(
                struct.unpack(MPQUserDataHeader.struct_format, data))
            header = header._asdict()
            header['content'] = self.file.read(header['user_data_header_size'])
            return header

        magic = self.file.read(4)
        self.file.seek(0)
        
        print(magic)
        
        if magic == "HM3W":
            datReader = DataReader(self.file)
            header = {}
            ## should be HM3W
            header["wc3map_magic"] = datReader.charArray(4)
            
            ## unknown
            datReader.int()
            header["wc3map_mapName"] = datReader.string()
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
            self.file.read(512 - datReader.index)
        else:
            ## If the magic isn't HM3W, we will skip the first 512 bytes of the 
            ## file anyway 
            self.file.seek(512)
            
        print(self.file.tell())
        magic = self.file.read(4)
        self.file.seek(512)
        print(magic)
        
        if magic == b'MPQ\x1a':
            header.update(read_mpq_header())
            header['offset'] = 512
        elif magic == b'MPQ\x1b':
            user_data_header = read_mpq_user_data_header()
            header.update(read_mpq_header(user_data_header['mpq_header_offset']))
            header['offset'] = user_data_header['mpq_header_offset']
            header['user_data_header'] = user_data_header
            
        else:
            raise ValueError("Invalid file header.")

        return header
    
    def extract_files(self, filenames, folder = ""):
        """Extract given files from the archive to disk."""
        ## Modification: Can extract files to a folder
        if folder != "":
            path = folder+"/"
        else:
            path = ""
            
        for filename in filenames:
            data = self.read_file(filename)
            f = open(path+filename, 'wb')
            f.write(data or "")
            f.close()

def main():
    import argparse
    description = "mpyq reads and extracts MPQ archives."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("file", action="store", help="path to the archive")
    parser.add_argument("-I", "--headers", action="store_true", dest="headers",
                        help="print header information from the archive")
    parser.add_argument("-H", "--hash-table", action="store_true",
                        dest="hash_table", help="print hash table"),
    parser.add_argument("-b", "--block-table", action="store_true",
                        dest="block_table", help="print block table"),
    parser.add_argument("-s", "--skip-listfile", action="store_true",
                        dest="skip_listfile", help="skip reading (listfile)"),
    parser.add_argument("-t", "--list-files", action="store_true", dest="list",
                        help="list files inside the archive")
    parser.add_argument("-x", "--extract", action="store_true", dest="extract",
                        help="extract files from the archive")
    args = parser.parse_args()
    if args.file:
        if not args.skip_listfile:
            archive = MPQArchive(args.file)
        else:
            archive = MPQArchive(args.file, listfile=False)
        if args.headers:
            archive.print_headers()
        if args.hash_table:
            archive.print_hash_table()
        if args.block_table:
            archive.print_block_table()
        if args.list:
            archive.print_files()
        if args.extract:
            archive.extract_to_disk()


if __name__ == '__main__':
    main()
