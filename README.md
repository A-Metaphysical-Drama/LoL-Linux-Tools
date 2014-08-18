# Warning: This project is discontinued since patching wine is a better solution. You can patch it with this hack: http://pastebin.com/Nqj1f0z0

League of Legends Linux Tools
===============

League of Legends Linux Tools is an open source application made to edit and repair League of Legends Files in a linux environment.

Installation
------------------------
1. Clone repository:

    git clone git://github.com/A-Metaphysical-Drama/LoL-Linux-Tools.git

2. Edit config.py with your path to League of Legends directory (The one containing RADS subdir)
Example:

    lol_path = '/home/user/League_of_Legends'

Usage
------------------------
From the application directory run:

    $ ./lol_linux.py command

The available commands are:

1. texture_patch - Patches League of Legend with non-mipmapped textures, this will fix game crashing at the Item Shop opening. Makes a backup of the edited files in the ./backups directory

2. repair - This will check game files for corrupted (Or modified) ones, repairing is not yet implemented

3. info - This will print some informations about the game version and so on - It's not yet implemented

Note: League of Legends Linux Tools is made for *Python 3* but should work in Python 2 as well

Warning!
------------------------
This application may damage files! Even though i tested it, i'm not responsible for any damage caused by the use of this application.

License
------------------------
    Copyright (c) 2012, A Metaphysical Drama

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

