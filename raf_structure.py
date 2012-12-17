import struct
import zlib
import os
import re
import hashlib
from functions import *
from constants import *

class Path:
    def __init__(self, offset, size, string):
        self.offset = offset
        self.size = size
        self.string = string
        self.hash = string_hash(string)
    def __str__(self):
        return " Path:" + \
             "\n        Offset: " + str(self.offset) + \
             "\n          Size: " + str(self.size) + \
             "\n        String: " + self.string + \
             "\n          Hash: " + str(self.hash)

class File:
    def __init__(self, p_hash, offset, size, p_index):
        self.p_hash = p_hash
        self.offset = offset
        self.size = size
        self.p_index = p_index
    def __str__(self):
        return " File:" + \
             "\n     Path Hash: " + str(self.p_hash) + \
             "\n        Offset: " + str(self.offset) + \
             "\n          Size: " + str(self.size) + \
             "\n    Path Index: " + str(self.p_index)

class Raf:
    def __init__(self, path):
        self.path = path
        self.file = None
        self.header = b''
        self.flist = b''
        self.plist = b''
        self.version = 1
        self.m_index = 0
        self.flist_offset = 20
        self.plist_offset = 0
        self.file_entries = 0
        self.files = []
        self.path_size = 0
        self.path_entries = 0
        self.paths = []

        self.data_path = path + '.dat'
        self.data_file = None

    def save(self):
        self.file = open(self.path, 'wb')
        self.file.write(self.header)
        self.file.write(self.flist)
        self.file.write(self.plist)
        self.file.close()

    def read(self):
        self.file = open(self.path, 'rb')
        if self.file.read(4) != MAGIC:
            print("Error: This is not a RAF File!")
            exit(1)
        self.version = self.read_uint32()
        if self.version != VERSION:
            print("Error: This file version (", version, ") is not supported!")
            exit(1)
        self.m_index = self.read_uint32()
        self.flist_offset = self.read_uint32()
        self.plist_offset = self.read_uint32()
        self.file_entries = self.read_uint32()
        for e in range(0, self.file_entries):
            self.files.append(File(self.read_uint32(), self.read_uint32(), self.read_uint32(), self.read_uint32()))
        self.path_size = self.read_uint32()
        self.path_entries = self.read_uint32()
        for e in range(0, self.path_entries):
            tmp_offset = self.read_uint32()
            self.paths.append(Path(tmp_offset, self.read_uint32(), self.read_string_at(tmp_offset + self.plist_offset)))
        self.data_file = RafData(self.data_path, False)

    def unpack(self, path):
        for i in self.files:
            file_dir, file_name = os.path.split(self.paths[i.p_index].string)
            try:
                os.makedirs(os.path.join(path, file_dir))
            except:
                pass
            #print(os.path.join(path, file_dir, file_name))
            self.data_file.extract_file(i.offset, i.size, os.path.join(path, file_dir, file_name))

    def make_from_dirtree(self, base_path, rlsm):
        self.data_file = RafData(self.data_path, True)
        for dirname, dirnames, filenames in os.walk(base_path):
            for filename in filenames:
                file_path = os.path.join(dirname, filename)
                raf_path = re.sub(base_path + '/', '', file_path)
                # Files in the root path will be skipped
                if not '/' in raf_path:
                    continue
                compress = True
                extension = os.path.splitext(raf_path)[1].lower()
                if extension == ".gfx" or extension == ".fsb" or extension == ".fev":
                    file_info = rlsm.find_file(raf_path)
                    if file_info:
                        compress = file_info.is_compressed()
                    else:
                        compress = False

                file_offset, file_size = self.data_file.add_file(file_path, compress)
                path_hash = string_hash(raf_path)
                path_size = len(raf_path) + 1
                path_index = len(self.paths)
                self.paths.append(Path(0, path_size, raf_path))
                self.files.append(File(path_hash, file_offset, file_size, path_index))
        self.data_file.close()
        self.make_flist()
        self.make_plist()
        self.make_header()

    def check(self):
        error = 0
        if len(self.files) != self.file_entries:
            print('Err.no. 1')
            error += 1
        if len(self.paths) != self.path_entries:
            print('Err.no. 2')
            error += 1
        if self.plist_offset != (4 + self.file_entries * 16 + self.flist_offset):
            print('Err.no. 3')
            error += 1
        if (self.plist_offset + self.path_size) != os.path.getsize(self.path):
            print('Err.no. 4')
            error += 1

        last_hash = 0
        dat_size = 0
        for f in self.files:
            dat_size += f.size
            if self.paths[f.p_index].hash != f.p_hash:
                print('Err.no. 5')
                error += 1
            if f.p_hash < last_hash:
                print('Err.no. 6')
                error += 1
            last_hash = f.p_hash
        if dat_size != os.path.getsize(self.path + '.dat'):
            print('Err.no. 7')
            error += 1

        print(str(error) + " errors found!")

    def find_file(self, path):
        hash = string_hash(path)

        for f in self.files:
            if f.p_hash == hash:
                if self.paths[f.p_index].string == path:
                    return f
                else:
                    continue
            else:
                continue
        return None

        # This is a faster code but it may fail in case of strings with identical hashes, needs tweaks
        """
        k_min = 0
        k_max = len(self.files)
        k = int((k_min+k_max)/2)
        while True:
            if self.files[k].p_hash == hash:
                return self.files[k]
            elif self.files[k].p_hash < hash:
                k_min = k
            else: #self.files[k].p_hash > hash:
                k_max = k

            if k == int((k_min+k_max)/2):
                return None
            k = int((k_min+k_max)/2)
        """

    def pack_uint32(self, uint):
        return struct.pack(b'<I', uint)

    def pack_string(self, string):
        string = string.encode('ascii')
        return string + b'\x00'

    def read_uint32(self):
        if not self.file:
            return 0
        return struct.unpack(b'<I', self.file.read(4))[0]

    def read_string(self):
        string = b''
        if not self.file:
            return string
        while 1:
            c = self.file.read(1)
            if c == b'\x00' or not c:
                break
            string += c
        return string.decode("ascii")

    def read_string_at(self, pos):
        tmp = self.file.tell()
        self.file.seek(pos)
        string = self.read_string()
        self.file.seek(tmp)
        return string

    def make_header(self):
        self.header += MAGIC
        self.header += self.pack_uint32(self.version)
        self.header += self.pack_uint32(self.m_index)
        self.header += self.pack_uint32(self.flist_offset)
        self.header += self.pack_uint32(self.plist_offset)

    def make_flist(self):
        self.files.sort(key=lambda f: f.p_hash)

        self.file_entries = len(self.files)
        self.flist += self.pack_uint32(self.file_entries)
        for f in self.files:
            self.flist += self.pack_uint32(f.p_hash)
            self.flist += self.pack_uint32(f.offset)
            self.flist += self.pack_uint32(f.size)
            self.flist += self.pack_uint32(f.p_index)

    def make_plist(self):
        for i in range(0, len(self.paths)):
            if i == 0:
                offset = len(self.paths)*8 + 8
            else:
                offset = self.paths[i-1].offset + self.paths[i-1].size
            self.paths[i].offset = offset

        string_data = b''
        plist_data = b''
        self.plist_offset = self.flist_offset + len(self.flist)
        self.path_entries = len(self.paths)

        for p in self.paths:
            plist_data += self.pack_uint32(p.offset)
            plist_data += self.pack_uint32(p.size)
            string_data += self.pack_string(p.string)
        self.path_size = len(plist_data) + len(string_data) + 8
        self.plist = self.pack_uint32(self.path_size) + self.pack_uint32(self.path_entries) + plist_data + string_data

class RafData:
    def __init__(self, path, write=False):
        self.path = path
        self.file = None
        self.write = write
        if write:
            self.file = open(self.path, 'wb')
        else:
            self.file = open(self.path, 'rb')

    def close(self):
        self.file.close()

    def add_file(self, path, compress):
        if not self.write:
            print('RafData si in read only mode.')
            exit(1)

        f = open(path, 'rb')
        file_offset = self.file.tell()

        compobj = None
        if compress:
            compobj = zlib.compressobj(6)

        while True:
            data = f.read(BUFFER_LEN)
            if data == b'':
                break
            if compobj:
                self.file.write(compobj.compress(data))
            else:
                self.file.write(data)
        if compobj:
            self.file.write(compobj.flush())

        file_size = self.file.tell() - file_offset
        #print('Added file:', path, 'Size:', file_size, 'Offset:', file_offset)
        return file_offset, file_size

    def get_file(self, offset, size):
        if self.write:
            print('RafData si in write only mode.')
            exit(1)

        data = b''
        self.file.seek(offset)
        decompobj = None
        if self.file.read(2) == ZLIB_HEAD:
            decompobj = zlib.decompressobj()
        self.file.seek(offset)

        while size > 0:
            if decompobj:
                data += decompobj.decompress(self.file.read(min(BUFFER_LEN, size)))
            else:
                data += self.file.read(min(BUFFER_LEN, size))
            size -= BUFFER_LEN

        if decompobj:
            data += decompobj.flush()

        return data

    def extract_file(self, offset, size, path):
        if self.write:
            print('RafData si in write only mode.')
            exit(1)

        out = open(path, 'wb')

        data = b''
        self.file.seek(offset)
        decompobj = None
        if self.file.read(2) == ZLIB_HEAD:
            decompobj = zlib.decompressobj()
        self.file.seek(offset)

        while size > 0:
            if decompobj:
                data = decompobj.decompress(self.file.read(min(BUFFER_LEN, size)))
            else:
                data = self.file.read(min(BUFFER_LEN, size))
            size -= BUFFER_LEN
            out.write(data)

        if decompobj:
            data = decompobj.flush()
            out.write(data)

        out.close()

    def get_file_md5(self, offset, size):
        data = self.get_file(offset, size)
        md5 = hashlib.md5(data).digest()
        return md5

