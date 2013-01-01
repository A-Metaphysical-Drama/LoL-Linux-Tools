# Copyright (c) 2012, A Metaphysical Drama
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import struct
import sys
import os
import re
import binascii
from constants import * 

class Dir:
    def __init__(self, name_index, subdir_index, subdir_count, file_index, file_count):
        self.name_index = name_index
        self.subdir_index = subdir_index
        self.subdir_count = subdir_count
        self.file_index = file_index
        self.file_count = file_count
    def __str__(self):
        return " Dir:" + \
             "\n    Name Index: " + str(self.name_index) + \
             "\n  SubDir Index: " + str(self.subdir_index) + \
             "\n  SubDir Count: " + str(self.subdir_count) + \
             "\n    File Index: " + str(self.file_index) + \
             "\n    File Count: " + str(self.file_count)

class File:
    def __init__(self, name_index, version, md5, flags, size, compressed_size, unk):
        self.name_index = name_index
        self.version = version
        self.md5 = md5
        self.flags = flags
        #   Flags:
        #       0x01 :  Managedfiles dir (?)
        #       0x02 :  Archived/Filearchives dir (?)
        #       0x04 :  (?)
        #       0x10 :  Compressed
        #   lol_air_client: all 0
        #   lol_air_client_config_euw: all 0
        #   lol_launcher: all & 4
        #   lol_game_client: all & 4
        #   lol_game_client_en_gb: all 5
        self.size = size
        self.compressed_size = compressed_size
        self.unk = unk # 0x?? 0x?? 0x?? 0x?? 0x?? 0x?? 0xcd 0x01

        self.path = ''

    def is_compressed(self):
        return self.flags & 0x10

    def is_archived(self):
        return self.flags & 0x02

    def __str__(self):
        return " File:" + \
             "\n    Name Index: " + str(self.name_index) + \
             "\n       Version: " + str(self.version) + \
             "\n      MD5 Hash: " + str(binascii.b2a_hex(self.md5)) + \
             "\n         flags: " + bin(self.flags) + \
             "\n          Size: " + str(self.size) + \
             "\n   Compr. Size: " + str(self.compressed_size) + \
             "\n           unk: " + str(binascii.b2a_hex(self.unk)) + \
             "\n          Path: " + self.path

class RLSM:
    def __init__(self, path):
        self.file = open(path, 'rb')
        if self.file.read(4) != RLSM_HEAD or self.file.read(4) != RLSM_MAGIC:
            print("Invalid Releasemanifest file format")
            exit(1)

        self.entries = self.read_uint32()
        self.version = self.read_uint32()

        # Dirs
        self.dir_count = self.read_uint32()
        self.dirs = []

        for k in range(0, self.dir_count):
            self.dirs.append(Dir(self.read_uint32(), self.read_uint32(), self.read_uint32(), self.read_uint32(), self.read_uint32()))
            #print(self.dirs[k])

        # Files
        self.file_count = self.read_uint32()
        self.files = []

        for k in range(0, self.file_count):
            self.files.append(File(self.read_uint32(), self.read_uint32(), self.file.read(16), self.read_uint32(), self.read_uint32(), self.read_uint32(), self.file.read(8)))
            #print(self.files[k])

        # Strings
        self.string_count = self.read_uint32()
        self.string_size = self.read_uint32()
        self.strings = []

        # File Tree
        self.file_tree = []

        for k in range(0, self.string_count):
            self.strings.append(self.read_string())
            #print(self.strings[k])

    def make_file_tree(self, index=0, path=''):
        if self.dirs[index].subdir_index == 0:
            #print(path + self.strings[self.dirs[index].name_index])
            return
        for k in range(0, self.dirs[index].subdir_count):
            string_index = self.dirs[self.dirs[index].subdir_index + k].name_index
            sdir_path = path + '/' + self.strings[string_index]
            #print(sdir_path)
            self.make_file_tree(self.dirs[index].subdir_index + k, sdir_path)
        self.add_files_to_tree(index, path)

    def add_files_to_tree(self, index, path):
        for k in range(0, self.dirs[index].file_count):
            file = self.files[self.dirs[index].file_index + k]
            self.file_tree.append(file)
            self.file_tree[-1].path = (path + '/' + self.strings[file.name_index])[1:]
            #print(path + '/' + self.strings[file.name_index])
            #if file.flags & (0x01 + 0x00):
            #if not file.flags & (0x02 + 0x00):
            #if file.flags != 5:
            #if file.size != 0:
            #    print(file)

    def find_file(self, path):
        path_array = []
        head = path
        while head:
            head,tail=os.path.split(head)
            path_array.append(tail)

        index = 0

        while True:
            name = path_array.pop()
            #print(name)
            last_index = index

            if len(path_array) == 0:
                for k in range(0, self.dirs[index].file_count):
                    string_index = self.files[self.dirs[index].file_index + k].name_index
                    if self.strings[string_index] == name:
                        return self.files[self.dirs[index].file_index + k]
                #print("Could not find File:", path)
                return None

            for k in range(0, self.dirs[index].subdir_count):
                string_index = self.dirs[self.dirs[index].subdir_index + k].name_index
                if self.strings[string_index] == name:
                    index = self.dirs[index].subdir_index + k
                    break

            if index == last_index:
                #print("Could not find File:", path)
                return None

    def match_file(self, name):
        matched = []
        if not self.file_tree:
            self.make_file_tree()

        for f in self.file_tree:
            if f.path.find(name) >= 0:
                matched.append(f)

        return matched

    def read_uint32(self):
        if not self.file:
            return 0
        return struct.unpack('<I', self.file.read(4))[0]

    def read_string(self):
        if not self.file:
            return ''
        string = b''
        while 1:
            c = self.file.read(1)
            if c == b'\x00' or not c:
                break
            string += c
        return string.decode("ascii")

    def __str__(self):
        return "Releasemanifest:" + \
             "\n  Entries: " + str(self.entries) + \
             "\n  Version: " + str(self.version) + \
             "\n     Dirs: " + str(self.dir_count) + \
             "\n    Files: " + str(self.file_count) + \
             "\n  Strings: " + str(self.string_count)
