#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Cournal.
# Copyright (C) 2012 Fabian Henze
# 
# Cournal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cournal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Cournal.  If not, see <http://www.gnu.org/licenses/>.

import string

# List of all characters that are allowed in filenames. Must not contain ; and :
valid_characters = string.ascii_letters + string.digits + ' _()+,.-=^~'

def filename_to_docname(filename):
    """
    Convert the filename of a saved document to a documentname. Filenames have the
    form "cnl-[documentname].save" where [documentname] is the name of the
    document with escaped special characters

    Positional arguments:
    filename -- Name of the file with escaped special characters

    Return value: Name of the document without escaped special characters.
    """
    result = ""
    input = StringIO(filename[4:-5])

    while True:
        char = input.read(1)
        if char == "":
            break
        elif char == ':':
            charcode = ""
            while len(charcode) == 0 or charcode[-1] != ';':
                charcode += input.read(1)
            char = chr(int(charcode[:-1], 16))
        result += char

    return result

def docname_to_filename(name):
    """
    Convert the name of a document to a valid filename. Filenames have the
    form "cnl-[documentname].save" where [documentname] is the name of the
    document with escaped special characters.
    
    Positional arguments:
    name -- Name of the document without escaped special characters.
    
    Return value: Name of the file with escaped special characters
    """
    result = ""

    for char in name:
        if char in valid_characters:
            result += char
        else:
            result += ":" + hex(ord(char))[2:] + ";"

    return "cnl-" + result + ".save"