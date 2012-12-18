# Raf
MAGIC      = b'\xf0\x0e\xbe\x18'
VERSION    = 1
ZLIB_HEAD  = b'\x78\x9c'

# Releasemanifest
RLSM_HEAD  = b'\x52\x4c\x53\x4d'
RLSM_MAGIC = b'\x01\x00\x01\x00'

# Buffer for reading/writing
BUFFER_LEN = 4096

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

