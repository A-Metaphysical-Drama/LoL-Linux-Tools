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

# Raf
MAGIC      = b'\xf0\x0e\xbe\x18'
VERSION    = 1
ZLIB_HEAD  = b'\x78\x9c'

# Releasemanifest
RLSM_HEAD  = b'\x52\x4c\x53\x4d'
RLSM_MAGIC = b'\x01\x00\x01\x00'

# Buffer for reading/writing
BUFFER_LEN = 32768

# Directories
import os

# Downloads
dl_dir = os.path.join(os.curdir, 'downloads')
if not os.path.isdir(dl_dir):
    os.mkdir(dl_dir)

# Backups
bk_dir = os.path.join(os.curdir, 'backups')
if not os.path.isdir(bk_dir):
    os.mkdir(bk_dir)

# Temp
tmp_dir = os.path.join(os.curdir, 'temp')
if not os.path.isdir(tmp_dir):
    os.mkdir(tmp_dir)

