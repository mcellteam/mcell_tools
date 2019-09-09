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
from build_settings import *


def get_cmake_build_type_arg(opts):
    if opts.debug:
        build_type = 'Debug'
    else:
        build_type = 'Release'

    return '-DCMAKE_BUILD_TYPE=' + build_type


def build_mcell(opts):

    mcell_build_dir = os.path.join(opts.work_dir, BUILD_DIR_MCELL)
    if opts.clean:
        # TODO
        log("Dry clean of " + mcell_build_dir)
    
    
    log("Running mcell build...")
    
    # create working directory
    if not os.path.exists(mcell_build_dir):
        os.makedirs(mcell_build_dir)
    
    # setup cmake build arguments
    cmd_cmake = ['cmake']
    cmd_cmake.append(os.path.join(opts.top_dir, REPO_NAME_MCELL))

    cmd_cmake.append(get_cmake_build_type_arg(opts))

    if BUILD_OPTS_USE_LTO:
        cmd_cmake.append('-DUSE_LTO=ON')
        
    # run cmake
    ec = run(cmd_cmake, mcell_build_dir)
    check_ec(ec, cmd_cmake)
    
    # setup make build arguments
    cmd_make = ['make']
    cmd_make.append('-j' + str(int(multiprocessing.cpu_count()/2))) 
    
    # run make 
    ec = run(cmd_make, mcell_build_dir, timeout_sec = BUILD_TIMEOUT)
    check_ec(ec, cmd_make)
    
    return mcell_build_dir
        

def build_cellblender(opts):
    
    cellblender_build_dir = os.path.join(opts.work_dir, BUILD_DIR_CELLBLENDER)
    if opts.clean:
        # TODO
        log("Dry clean of " + cellblender_build_dir)

    # create working directory
    if not os.path.exists(cellblender_build_dir):
        os.makedirs(cellblender_build_dir)
        
            # setup make build arguments
    cmd_make = ['make', '-f', 'makefile', 'install', 
         'INSTALL_DIR=' +  cellblender_build_dir ]
    
    # run make (in-source build)
    ec = run(cmd_make, os.path.join(opts.top_dir, REPO_NAME_CELLBLENDER), timeout_sec = BUILD_TIMEOUT)
    check_ec(ec, cmd_make)
    
    return cellblender_build_dir


def build_gamer(opts):
    gamer_build_dir = os.path.join(opts.work_dir, BUILD_DIR_GAMER)
    gamer_install_dir = os.path.join(opts.work_dir, INSTALL_DIR_GAMER)
    if opts.clean:
        # TODO
        log("Dry clean of " + gamer_build_dir)
        log("Dry clean of " + gamer_install_dir)
    
    
    log("Running gamer build...")
    
    # create working directory
    if not os.path.exists(gamer_build_dir):
        os.makedirs(gamer_build_dir)
    
    # setup cmake build arguments
    cmd_cmake = ['cmake']
    cmd_cmake.append(os.path.join(opts.top_dir, REPO_NAME_GAMER))
    cmd_cmake.append(get_cmake_build_type_arg(opts))
    cmd_cmake.append('-DCMAKE_INSTALL_PREFIX:PATH=' + gamer_install_dir)
        
    # library casc requires __has_cpp_attribute c++17 - disable it
    # maybe we can check gcc versio nan enable it but let's keep it simple for now
    cmd_cmake.append('-DCMAKE_CXX_FLAGS=-D\'__has_cpp_attribute(x)=0\'')
        
    # run cmake
    ec = run(cmd_cmake, gamer_build_dir, timeout_sec = BUILD_TIMEOUT)
    check_ec(ec, cmd_cmake)
    
    # setup make build arguments
    cmd_make = ['make', 'install']
    cmd_make.append('-j' + str(int(multiprocessing.cpu_count()/2))) 
    
    # run make 
    ec = run(cmd_make, gamer_build_dir, timeout_sec = BUILD_TIMEOUT)
    check_ec(ec, cmd_make)
    
    return gamer_install_dir
        

def build_all(opts):
    build_dirs = {}
    
    build_dirs[REPO_NAME_MCELL] = build_mcell(opts)
    
    # in-source build for now, should be fixed but it can work like this
    build_dirs[REPO_NAME_CELLBLENDER] = build_cellblender(opts)
    
    
    build_gamer(opts)
    
    return build_dirs
    