#!/usr/bin/env python3

"""
Copyright (C) 2019 by
The Salk Institute for Biological Studies and
Pittsburgh Supercomputing Center, Carnegie Mellon University

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
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
from options import *
from utils import fatal_error

def print_help():
    print("Usage: mcell_git [clone|checkout|pull|push|reset-hard])")


if __name__ == "__main__":
    argc = len(sys.argv) 
    if argc == 1 or sys.argv[1] == "help":
        print_help()
        sys.exit(0)     
    
    a1 = sys.argv[1]
    
    opts = Options()
    opts.use_private_repos = True
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

    elif a1 == 'reset-hard':
        if argc > 2:
            fatal_error("Command reset-hard does not have any extra arguments")
        print("Reseting all repositories")
        repositories.reset_hard(opts)

    elif a1 == 'tag':
        if argc == 3:
            # misusing branch argument for tag
            opts.branch = sys.argv[2]
        else:
            fatal_error("Missing tag argument")
        print("Tagging all repositories")
        repositories.tag(opts)
    
    else:
        print("Error: unknown command '" + a1 + "'")
        print_help()

