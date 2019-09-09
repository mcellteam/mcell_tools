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

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(THIS_DIR, 'scripts'))

# TODO: check whether scripts. notation works
import repositories
import build
import bundle

from utils import log, fatal_error, get_cwd_no_link
from build_settings import *

sys.path.append(os.path.join(THIS_DIR, '..', 'mcell_tests'))
import run_tests


class Options:
    def __init__(self):
        self.update = False
        self.clean = False
        self.ignore_dirty = False
        self.debug = False
        
        self.do_repos = False
        self.do_build = False
        self.do_bundle = False
        self.do_test = False
        
        self.branch = DEFAULT_BRANCH
        
        # using os.getcwd() + '..' does not work with links as expected
        self.top_dir = os.path.dirname(get_cwd_no_link())
        self.work_dir = os.path.join(self.top_dir, REPO_NAME_MCELL_TOOLS, WORK_DIR_NAME)

    def __repr__(self):
        attrs = vars(self)
        return ", ".join("%s: %s" % item for item in attrs.items())
            

def create_argparse():
    parser = argparse.ArgumentParser(description='MCell & CellBlender build tool')
    # NOTE: maybe add verbosity level? - for now, all information is printed out 
    parser.add_argument('-u', '--update', action='store_true', help='update repositories is they are alread checked out')
    parser.add_argument('-c', '--clean', action='store_true', help='clean data from previous build')
    parser.add_argument('-i', '--ignore-dirty', action='store_true', help='ignore dirty repositories')
    parser.add_argument('-d', '--debug', action='store_true', help='build debug variant of mcell')

    parser.add_argument('-b', '--branch', type=str, help='branch to checkout, tries to change the current branch if the branch is different from what is selected and there are no changes')

    parser.add_argument('-q', '--do-repos', action='store_true', help='get repositories (done by default when none of "qwer" args are set)')
    parser.add_argument('-w', '--do-build', action='store_true', help='run build (done by default when none of "qwer" args are set)')
    parser.add_argument('-e', '--do-bundle', action='store_true', help='build bundle (done by default when none of "qwer" args are set)')
    parser.add_argument('-r', '--do-test', action='store_true', help='run tests (done by default when none of "qwer" args are set)')
    return parser


def process_opts():
    
    parser = create_argparse()
    args = parser.parse_args()
    print(args)
    
    opts = Options()
    
    if args.update:
        opts.update = True
    if args.clean:
        opts.clean = True
    if args.ignore_dirty:
        opts.ignore_dirty = True
    if args.debug:
        opts.debug = True
        
    if args.branch:
        opts.branch = args.branch
                
    opts.do_repos = args.do_repos
    opts.do_build = args.do_build
    opts.do_bundle = args.do_bundle
    opts.do_test = args.do_test
    
    # no specific task was set, do all
    if not (opts.do_repos or opts.do_build or opts.do_bundle or opts.do_test):
        opts.do_repos = True
        opts.do_build = True
        opts.do_bundle = True
        opts.do_test = True

    return opts
    

def check_prerequisites():
    if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 5):
        # this is what cellblender was using, not sure, maybe just version 3.* suffices 
        fatal_error("Error: Required Python version is at least 3.5")
    
    # bzip2
    
    
def test_all(install_dirs):    
    # running test within the same python instance
    run_tests.run_tests(install_dirs)


if __name__ == "__main__":
     
    opts = process_opts()
    print(opts)
    
    check_prerequisites()

    log("Top directory: " + opts.top_dir)

    # 1) get all the sources, update them optionally
    if opts.do_repos:
        repositories.get_or_update(opts)
    
    # 2) build
    # returns dictionary  repo name -> where it was built
    if opts.do_build:
        install_dirs = build.build_all(opts)
    else:
        # testing will use defaults
        install_dirs = {}
    
    # 3_ create bundle
    # overwrite install_dirs with new values
    if opts.do_bundle:
        bundle_archive = bundle.create_bundle(opts)
        # also extract it right away if testing is needed
        if opts.do_test:
            install_dirs = bundle.extract_resulting_bundle(bundle_archive)
    
    # 4) test
    if opts.do_test:
        test_all(install_dirs)
    
    log("--- All tasks finished successfully ---")
    