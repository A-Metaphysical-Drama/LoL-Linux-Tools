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

from __future__ import absolute_import, print_function, unicode_literals
import os

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

from constants import *

def ver_to_int(ver):
    version_int = ver.split('.')
    version_int = (int(version_int[0])<<24) | (int(version_int[1])<<16) | (int(version_int[2])<<8) | int(version_int[3])
    return version_int

def int_to_ver(n):
    version_str = str((n>>24)&0xFF)
    version_str = version_str + '.' + str((n>>16)&0xFF)
    version_str = version_str + '.' + str((n>>8)&0xFF)
    version_str = version_str + '.' + str(n&0xFF)
    return version_str

def string_hash(str):
    hash = 0
    temp = 0
    for character in str:
        hash = (hash << 4) + ord(character.lower())
        temp = hash & 0xf0000000
        if temp != 0:
            hash = hash ^ (temp >> 24)
            hash = hash ^ temp
    return hash

def get_filearchives(path):
    filearchives = {}
    for f in os.listdir(path):
        if f.lower() == "rads":
            rads_dir = f
            break
    path = os.path.join(path, rads_dir, 'projects', 'lol_game_client', 'filearchives')
    versions = os.listdir(path)
    for version in versions:
        version_int = ver_to_int(version)
        files = os.listdir(os.path.join(path, version))
        for filename in files:
            file_path = os.path.join(path, version, filename)
            ext = os.path.splitext(file_path)[1]
            if ext == '.raf':
                filearchives[version_int] = file_path
    return filearchives

def get_last_releasemanifest(path):
    for f in os.listdir(path):
        if f.lower() == "rads":
            rads_dir = f
            break
    path = os.path.join(path, rads_dir, 'projects', 'lol_game_client', 'releases')
    versions = os.listdir(path)
    max_version = 0
    for version in versions:
        version_int = version.split('.')
        version_int = (int(version_int[0])<<24) | (int(version_int[1])<<16) | (int(version_int[2])<<8) | int(version_int[3])
        if max_version < version_int:
            max_version = version_int
            rlsm = os.path.join(path, version, 'releasemanifest')
    return rlsm

def download_file(url):
    u = urlopen(url)
    file_name = url.split('/')[-1]

    file_path = os.path.join(dl_dir, file_name)
    try:
        file_size = int(u.getheader("Content-Length"))
    except AttributeError:
        file_size = int(u.info().getheaders("Content-Length")[0])
    print("Downloading", file_name, "Size:", str(file_size/1000) + 'kb')
    f = open(file_path, 'wb')
    file_size_dl = 0
    while True:
        buffer = u.read(BUFFER_LEN)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print(status, end="\r")

    f.close()
    print('')
    return file_path
