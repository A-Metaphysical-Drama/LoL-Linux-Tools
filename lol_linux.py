#!/usr/bin/env python
from __future__ import absolute_import, print_function, unicode_literals
import os
import re
import sys
import shutil
import tarfile
import hashlib
import datetime
from config import * 
from functions import *
from constants import *
import rlsm_structure as rlsm
import raf_structure as raf

def apply_patch(path, rlsm_file, filearchives):
    needed_versions = []
    print('Unpacking Archives, please wait...')
    for dirname, dirnames, filenames in os.walk(os.path.join(path, 'DATA')):
        for filename in filenames:
            file_path = os.path.join(dirname, filename)
            raf_path = re.sub(path + '/', '', file_path)
            file_info = rlsm_file.find_file(raf_path)
            if not file_info:
                print("File not found in releasemanifest, patch could not be applied.")
                exit(1)
            version_dir = os.path.join(path, 'filearchives', int_to_ver(file_info.version), 'raf_archive')
            if not file_info.version in needed_versions:
                needed_versions.append(file_info.version)
                raf_file = raf.Raf(filearchives[file_info.version])
                raf_file.read()
                raf_file.unpack(version_dir)
            shutil.copyfile(file_path, os.path.join(version_dir, raf_path))
            #print(file_path)
            #print(os.path.join(path, 'filearchives', int_to_ver(file_info.version), raf_path))

    print('Saving Backups, please wait...')
    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    for version in needed_versions:
        backup_dir = os.path.join(bk_dir, timestamp, int_to_ver(version))
        file_name = os.path.split(filearchives[version])[1]
        backup_file = os.path.join(backup_dir, file_name)
        try:
            os.makedirs(backup_dir)
        except:
            pass
        shutil.copyfile(filearchives[version], backup_file)
        shutil.copyfile(filearchives[version] + '.dat', backup_file + '.dat')

    print('Repacking Archives, please wait...')
    for version in needed_versions:
        version_dir = os.path.join(path, 'filearchives', int_to_ver(version))
        file_name = os.path.split(filearchives[version])[1]
        new_raf = raf.Raf(os.path.join(version_dir, file_name))
        new_raf.make_from_dirtree(os.path.join(version_dir, 'raf_archive'), rlsm_file)
        new_raf.save()

    print('Checking New Archives, please wait...')
    for version in needed_versions:
        version_dir = os.path.join(path, 'filearchives', int_to_ver(version))
        file_name = os.path.split(filearchives[version])[1]
        new_file = os.path.join(version_dir, file_name)
        
        if os.path.getsize(new_file) != os.path.getsize(filearchives[version]):
            print(new_file, 'size does not match the original one!')
            exit(1)

        test_1 = raf.Raf(new_file)
        test_2 = raf.Raf(filearchives[version])
        test_1.read()
        test_2.read()

        for i in range(0, len(test_1.files)):
            if test_1.files[i].p_hash != test_2.files[i].p_hash:
                print('Wrong Hash:', test_1.files[i], test_2.files[i])
                exit(1)
            if test_1.paths[test_1.files[i].p_index].string != test_2.paths[test_2.files[i].p_index].string:
                print('Wrong Path:', test_1.paths[test_1.files[i].p_index].string, test_2.paths[test_2.files[i].p_index].string)
                exit(1)

        del test_1
        del test_2

    print('Moving Archives, please wait...')
    for version in needed_versions:
        version_dir = os.path.join(path, 'filearchives', int_to_ver(version))
        file_name = os.path.split(filearchives[version])[1]
        new_file = os.path.join(version_dir, file_name)

        os.remove(filearchives[version])
        os.remove(filearchives[version] + '.dat')
        shutil.move(new_file, filearchives[version])
        shutil.move(new_file + '.dat', filearchives[version] + '.dat')

    print('Cleaning up, please wait...')
    shutil.rmtree(tmp_dir)
    print('Patch applied Successfully!')

def check_md5(rlsm_file, filearchives):
    rlsm_file.make_file_tree()
    raf_archives = {}
    bad_files = []

    for f in rlsm_file.file_tree:
        if (f.is_archived()):
            #print('Checking:', f.path)
            if not f.version in raf_archives:
                if not f.version in filearchives:
                    print(f)
                    continue
                raf_archives[f.version] = raf.Raf(filearchives[f.version])
                raf_archives[f.version].read()
            check = raf_archives[f.version].check_file_md5(f.path, f.md5)
            if not check:
                print('Bad File:', f.path)
                bad_files.append(f)

    return bad_files

print('League of Legends - Linux Tools')

# Checking for LoL dir
files = os.listdir(lol_path)
if not 'RADS' in files:
    print('"' + lol_path + '"', 'is not a valid League of Legends path, please edit config.py file!')
    exit(1)

if len(sys.argv) != 2:
    print('Usage:', sys.argv[0], "command")
    print('  Commands:')
    print('    texture_patch        - Patches LoL with non mipmapped item textures')
    print('    repair               - Checks filearchives and repairs corrupted files')
    print('    info                 - Prints various informations')
    exit(1)

if sys.argv[1] == 'texture_patch':
    data_url = 'http://www.darkwind.it/misc/DATA.tar.gz'
    data_file = download_file(data_url)
    tarfile.open(data_file).extractall(os.path.join(tmp_dir, 'texture_patch'))
    rlsm_file = rlsm.RLSM(get_last_releasemanifest(lol_path))
    filearchives = get_filearchives(lol_path)
    apply_patch(os.path.join(tmp_dir, 'texture_patch'), rlsm_file, filearchives)
elif sys.argv[1] == 'repair':
    rlsm_file = rlsm.RLSM(get_last_releasemanifest(lol_path))
    filearchives = get_filearchives(lol_path)
    print('Checking Files...')
    check_md5(rlsm_file, filearchives)
    print('Archive repair not yet implemented.')
elif sys.argv[1] == 'info':
    print("Not Yet Implemented")
else:
    print(sys.argv[1], 'is not a valid command.')

