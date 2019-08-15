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
import multiprocessing
from utils import *
from settings import *


def build_mcell(work_dir, opts):

    mcell_build_dir = os.path.join(work_dir, BUILD_DIR_MCELL)
    if opts.clean:
        # TODO
        log("Dry clean of " + mcell_build_dir)
    
    
    log("Running mcell build...")
    
    # create working directory
    if not os.path.exists(mcell_build_dir):
        os.makedirs(mcell_build_dir)
    
    # setup cmake build arguments
    cmake_cmd = ['cmake']
    cmake_cmd.append(os.path.join(opts.top_dir, REPO_NAME_MCELL))
    
    if opts.debug:
        build_type = 'Debug'
    else:
        build_type = 'Release'
        if BUILD_OPTS_USE_LTO:
            cmake_cmd.append('-DUSE_LTO=ON')
        
    cmake_cmd.append('-DCMAKE_BUILD_TYPE=' + build_type)
        
    # run cmake
    ec = run(cmake_cmd, mcell_build_dir)
    check_ec(ec, cmake_cmd)
    
    # setup make build arguments
    make_cmd = ['make']
    make_cmd.append('-j' + str(int(multiprocessing.cpu_count()/2))) 
    
    # run make 
    ec = run(make_cmd, mcell_build_dir, timeout_sec = BUILD_TIMEOUT)
    check_ec(ec, make_cmd)
        

def build_cellblender(work_dir, opts):
    
    cellblender_build_dir = os.path.join(work_dir, BUILD_DIR_CELLBLENDER)
    if opts.clean:
        # TODO
        log("Dry clean of " + cellblender_build_dir)

    # create working directory
    if not os.path.exists(cellblender_build_dir):
        os.makedirs(cellblender_build_dir)
        
            # setup make build arguments
    make_cmd = ['make', '-f', 'makefile', 'install', 
         'INSTALL_DIR=' +  cellblender_build_dir ]
    
    # run make (in-source build)
    ec = run(make_cmd, os.path.join(opts.top_dir, REPO_NAME_CELLBLENDER), timeout_sec = BUILD_TIMEOUT)
    check_ec(ec, make_cmd)
    

def build_all(opts):
    work_dir = os.path.join(get_cwd_no_link(), WORK_DIR_NAME)
    build_mcell(work_dir, opts)
    
    # in-source build for now, should be fixed but it can work like this
    build_cellblender(work_dir, opts)
    