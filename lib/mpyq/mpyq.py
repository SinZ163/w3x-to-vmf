#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import bz2
import os
import struct
import zlib

from io import BytesIO

## mpyq by Aku Kotkavuo, check LICENSE.txt
## Modification by Yoshi2 & SinZ
## Comments prefixed with ## were not made by the original author, 
## but added as part of the modification of this MPQ library
import logging

import mpyq_encryption
import mpyq_constants as const

from mpyq_compression import UnsupportedCompressionAlgorithm, decompress

__author__ = "Aku Kotkavuo"
__version__ = "0.2.4"

class MPQArchive(object):
    ## Initiate cryptographic functions for 
    ## hashing and decrypting data
    mpq_crypto = mpyq_encryption.MPQ_Crypto()
    _hash = mpq_crypto.hash
    _decrypt = mpq_crypto.decrypt
    
    def __init__(self, filename, listfile=True, strict = True, forceV1 = False):
        """Create a MPQArchive object.

        You can skip reading the listfile if you pass listfile=False
        to the constructor. The 'files' attribute will be unavailable
        if you do this.
        """
        self.strict = strict
        self.forceV1 = forceV1
        
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
        magic = self.file.read(4)
        self.file.seek(0)

        if magic == b'MPQ\x1a' or self.forceV1 == True:
            header = self.__read_mpq_header__()
            header['offset'] = 0
        elif magic == b'MPQ\x1b':
            user_data_header = self.__read_mpq_user_data_header__()
            header = read_mpq_header(user_data_header['mpq_header_offset'])
            header['offset'] = user_data_header['mpq_header_offset']
            
            header['user_data_header'] = user_data_header
        else:
            raise ValueError("Invalid file header.")

        return header
    
    def __read_mpq_header__(self, offset=None):
        if offset:
            self.file.seek(offset)
        data = self.file.read(32)
        
        header = const.MPQFileHeader._make(
                                        struct.unpack(const.MPQFileHeader.struct_format, 
                                                      data)
                                        )
        header = header._asdict()
        #print(header["format_version"])
        if header['format_version'] == 1:
            data = self.file.read(12)
            extended_header = const.MPQFileHeaderExt._make(
                                                           struct.unpack(
                                                                         const.MPQFileHeaderExt.struct_format, 
                                                                         data)
                                                           )
            header.update(extended_header._asdict())
            
        return header

    def __read_mpq_user_data_header__(self):
        data = self.file.read(16)
        header = const.MPQUserDataHeader._make(
                                               struct.unpack(const.MPQUserDataHeader.struct_format,
                                                             data)
                                               )
        header = header._asdict()
        header['content'] = self.file.read(header['user_data_header_size'])
        return header
    
    def read_table(self, table_type):
        """Read either the hash or block table of a MPQ archive."""

        if table_type == 'hash':
            entry_class = const.MPQHashTableEntry
        elif table_type == 'block':
            entry_class = const.MPQBlockTableEntry
        else:
            raise ValueError("Invalid table type.")

        table_offset = self.header['%s_table_offset' % table_type]
        table_entries = self.header['%s_table_entries' % table_type]
        key = self._hash('(%s table)' % table_type, 'TABLE')
        
        self.file.seek(table_offset + self.header['offset'])
        #print(table_offset, table_entries,self.header['offset'], "Oh my", key)
        data = self.file.read(table_entries * 16)
        data = self._decrypt(data, key)
        #print(len(data), table_entries)
        return [self.__unpack_entry__(entry_class, data, i) for i in xrange(table_entries)]
    
    def __unpack_entry__(self, entry_class, data, position):
        entry_data = data[position*16:position*16+16]
        
        if len(entry_data) == 0:
            return None
        
        return entry_class._make(
                               struct.unpack(entry_class.struct_format, 
                                             entry_data)
                               )
            
    def get_hash_table_entry(self, filename):
        """Get the hash table entry corresponding to a given filename."""
        hash_a = self._hash(filename, 'HASH_A')
        hash_b = self._hash(filename, 'HASH_B')
        for entry in self.hash_table:
            if (entry.hash_a == hash_a and entry.hash_b == hash_b):
                return entry
    
    def read_file(self, filename, force_decompress=False, raw = False):
        """Read a file from the MPQ archive."""
        
        if raw == True:
            fileparts = []
        
        hash_entry = self.get_hash_table_entry(filename)
        if hash_entry is None:
            return None
        
        block_entry = self.block_table[hash_entry.block_table_index]
        
        #print("______")
        #print("File {0} HashEntry Offset: {1} BlockEntry Offset: {2}".format(filename, hash_entry, block_entry))
        
        # Read the block.
        if block_entry.flags & const.MPQ_FILE_EXISTS:
            if block_entry.archived_size == 0:
                return None
            
            offset = block_entry.offset + self.header['offset']
            
            self.file.seek(offset)
            file_data = self.file.read(block_entry.archived_size)
            
            # File consist of many sectors. They all need to be
            # decompressed separately and united.
            sector_size = 512 << self.header['sector_size_shift']
            
            sectors = block_entry.size // sector_size + 1
            
            ## We calculate a sectorIndex value to be used in the
            ## decryption of the sector data. Basically, it should be the starting index
            ## of this particular sector.
            sectorIndex = (offset - self.header['offset']) // (sector_size)
            print("Sectorsize sectors sectorIndex offset sector size shift")
            print(sector_size, sectors, sectorIndex, offset, self.header['sector_size_shift'])
            
            print("{0} Filedata length: {1}".format(filename, len(file_data)))
            
            ## If file is encrypted, create the decryption key as explained 
            ## in the MPQ documentation on http://www.wc3c.net/tools/specs/QuantamMPQFormat.txt
            if block_entry.flags & const.MPQ_FILE_ENCRYPTED:
                ## The key is created by hashing the name of the file after
                ## removing the path that prefixes the filename. For this,
                ## we search for the position of the right-most backslash.
                backslash = filename.rfind("\\")
                if backslash != -1:
                    basekey = filename[backslash+1:]
                else:
                    basekey = filename
                
                key = self._hash(basekey, "TABLE")
                
                ## If the Fix_Key flag is set, we need to calculate the final key
                ## as '(base key + BlockOffset - ArchiveOffset) XOR FileSize'.
                if block_entry.flags & const.MPQ_FILE_FIX_KEY:
                    key = (key + offset - self.header['offset']) ^ block_entry.size
                    
            print("Implode: {0}, Compress: {1}, Encrypted: {2}, Fix Key: {3}".format(
                                                                                     (block_entry.flags & const.MPQ_FILE_IMPLODE) != 0, 
                                                                                     (block_entry.flags & const.MPQ_FILE_COMPRESS) != 0, 
                                                                                     (block_entry.flags & const.MPQ_FILE_ENCRYPTED) != 0, 
                                                                                     (block_entry.flags & const.MPQ_FILE_FIX_KEY) != 0)
                  )
            
            if not block_entry.flags & const.MPQ_FILE_SINGLE_UNIT:
                
                if block_entry.flags & const.MPQ_FILE_SECTOR_CRC:
                    ## The crc checksums are contained in the last sector.
                    crc = True
                    sectors += 1
                else:
                    crc = False
                
                ## If the file is encrypted, the sector offset table is encrypted, too.
                ## We need to decrypt it before being able to use it. Without the positions,
                ## we do not know where each sector of a compressed file starts.
                if block_entry.flags & const.MPQ_FILE_ENCRYPTED:
                    sectoroffset_table = file_data[0:(sectors+1)*4]
                    sectoroffset_table = self._decrypt(sectoroffset_table, key-1)
                    
                    positions = struct.unpack('<%dI' % (sectors + 1),
                                              sectoroffset_table)
                else:
                    positions = struct.unpack('<%dI' % (sectors + 1),
                                              file_data[:4*(sectors+1)])
                
                result = BytesIO()
                sector_bytes_left = block_entry.size
                
                #if raw == True:
                #    rawData = BytesIO()
                
                print(positions)
                for i in xrange(len(positions) - (2 if crc else 1)):
                    
                    ## Each sector is decrypted using the key + the 0-based index of the sector.
                    if block_entry.flags & const.MPQ_FILE_ENCRYPTED:
                        sectorModifier = i #+sectorIndex
                    else:
                        sectorModifier = 0
                        key = 0
                        
                    sector = file_data[positions[i]:positions[i+1]]
                    
                    ## We try to decrypt the sector data
                    if block_entry.flags & const.MPQ_FILE_ENCRYPTED and raw == False:
                        sector = self._decrypt(sector, key + sectorModifier)
                            
                    #if raw == True:
                    #    rawData.write(sector)
                    #else:
                    if (block_entry.flags & const.MPQ_FILE_COMPRESS and
                        (force_decompress or sector_bytes_left > len(sector)) and
                        raw == False):
                        
                        sector = decompress(sector, self.strict)
                            
                    elif raw:
                        sector_bytes_left -= len(sector)
                        fileparts.append((key+sectorModifier, sector))
                        
                    if not raw:
                        sector_bytes_left -= len(sector)
                        result.write(sector)
                        
                #if raw == True:
                #    file_data = rawData.getvalue()
                #else:
                file_data = result.getvalue()
            else:
                ## A single unit file should only contain a single sector, so we calculate
                ## the key simply as key + sectorIndex
                if block_entry.flags & const.MPQ_FILE_ENCRYPTED and raw == False:
                    #print("SingleUnit data length:", len(file_data))
                    sectorkey = key #+ sectorIndex
                    file_data = self._decrypt(file_data, sectorkey)
                elif raw == True:
                    sectorkey = 0

                # Single unit files only need to be decompressed, but
                # compression only happens when at least one byte is gained.
                if (block_entry.flags & const.MPQ_FILE_COMPRESS and
                    (force_decompress or block_entry.size > block_entry.archived_size) and
                    raw == False):
                    
                    file_data = decompress(file_data)
                    
                elif raw:
                    fileparts.append((sectorkey, file_data))
                    
            if raw:
                return fileparts
            else:
                return file_data
    
    ## A copy&paste of a bit of code from the read_file function
    ## allowing us to quickly check if a file exists.
    def file_exists(self, filename):
        hash_entry = self.get_hash_table_entry(filename)
        
        if hash_entry is None:
            return False
        
        block_entry = self.block_table[hash_entry.block_table_index]
        if block_entry.flags & const.MPQ_FILE_EXISTS:
            if block_entry.archived_size == 0:
                return False
            else:
                return True
        else:
            return False
            
            
            
    
