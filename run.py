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

import os
import sys
import subprocess
import argparse

sys.path.append(os.path.join(os.getcwd(), 'tools'))

import repositories
import build
from utils import log, get_cwd_no_link

#DEFAULT_BRANCH='development'
DEFAULT_BRANCH='testing_infrastructure'


class Options:
    def __init__(self):
        self.update = False
        self.clean = False
        self.debug = False
        self.branch = DEFAULT_BRANCH
        
        # using cwd + '..' does not work with links as expected
        self.top_dir = os.path.dirname(get_cwd_no_link())


def create_argparse():
    parser = argparse.ArgumentParser(description='MCell & CellBlender build tool')
    # NOTE: maybe add verbosity level? - for now, all information is printed out 
    parser.add_argument('-u', '--update', action='store_true', help='update repositories is they are alread checked out')
    parser.add_argument('-b', '--branch', type=str, help='branch to checkout, tries to change the current branch if the branch is different from what is selected and there are no changes')

    parser.add_argument('-c', '--clean', action='store_true', help='clean data from previous build')
    parser.add_argument('-d', '--debug', action='store_true', help='build debug variant of mcell')
    
    # NOTE: testing will require 
    parser.add_argument('-t', '--test', action='store_true', help='checkout and run tests')
    return parser


def process_opts():
    
    parser = create_argparse()
    args = parser.parse_args()
    
    opts = Options()
    
    if args.update:
        opts.update = True
    if args.clean:
        opts.clean = True
    if args.debug:
        opts.debug = True

    return opts
    

if __name__ == "__main__":
  
    opts = process_opts()
    
    log("Top directory: " + opts.top_dir)
    
    # 1) get all the sources, update them optionally
    repositories.get_or_update(opts)
    
    # 2) build
    #build.build_all(opts)
    
    # 3) test
    #if opts.test:
    #    test_all(opts)
    
    log("--- All tasks finished successfully ---")
    