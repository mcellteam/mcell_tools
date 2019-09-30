#!/usr/bin/env python3

"""
Copyright (C) 2019 by
The Salk Institute for Biological Studies and
Pittsburgh Supercomputing Center, Carnegie Mellon University

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

For the complete terms of the GNU General Public License, please see this URL:
http://www.gnu.org/licenses/gpl-2.0.html
"""

"""
This module gehaves similarly as git, it only operates on all 
relevant repositories.

Not all useful commands were implemented yet.
"""

import os
import sys

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(THIS_DIR, 'scripts'))

import repositories
from build_settings import *
from utils import fatal_error

def print_help():
    print("Usage: mcell_git [clone|checkout|pull|push])")


if __name__ == "__main__":
    argc = len(sys.argv) 
    if argc == 1 or sys.argv[1] == "help":
        print_help()
        sys.exit(0)     
    
    a1 = sys.argv[1]
    
    opts = Options()
    if a1 == 'clone' or a1 == 'checkout': 
        if argc == 3:
            opts.branch = sys.argv[2]
        
        print("Cloning or updating branch " + opts.branch + ".")
        repositories.get_or_update(opts)
    
    elif a1 == 'pull':
        if argc > 2:
            fatal_error("Command pull does not have any extra arguments")
        print("Pulling all repositories")
        repositories.pull(opts)
        
    elif a1 == 'push':
        if argc > 2:
            fatal_error("Command push does not have any extra arguments")
        print("Pushing all repositories")
        repositories.push(opts)
    
    else:
        print("Error: unknown command '" + a1 + "'")
        print_help()

