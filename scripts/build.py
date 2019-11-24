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
import platform
from utils import *
from build_settings import *


def get_cmake_build_type_arg(opts):
    if opts.debug:
        build_type = 'Debug'
    else:
        build_type = 'Release'

    return '-DCMAKE_BUILD_TYPE=' + build_type


def is_default_compiler_supported_by_mcell() -> bool:
    if platform.system() == 'Linux':
        cmd = ['gcc', '--version']
        res = run_with_ascii_output(cmd, cwd='.')
        if '8.3.0' in res:
            return False
        else:
            # TODO: some error check? maybe we will fix this issue 
            return True
    else:
        # for other OSes let's assume that everything is fine
        return True


def copy_cygwin_dlls(mcell_dir):
    dlls_path = os.path.join(MCELL_BUILD_INFRASTRUCTURE_DATA_DIR, CYGWIN_DLLS)
    files = [f for f in os.listdir(dlls_path) if os.path.isfile(os.path.join(dlls_path, f))]
    for f in files:
        dll = os.path.join(dlls_path, f)
        log("Copying '" + dll + "' to '" + mcell_dir + "'.");         
        shutil.copy(dll, mcell_dir)
        
        # cygwin also requires these libraries to be "executable"
        cmd_chmod = ['chmod', 'a+x', os.path.join(mcell_dir, '*.dll')]
        ec = run(cmd_chmod, shell=True)
        check_ec(ec, cmd_chmod)
    

def build_mcell(opts):

    mcell_build_dir = os.path.join(opts.work_dir, BUILD_DIR_MCELL)
    
    log("Running mcell build...")
    
    # create working directory
    if not os.path.exists(mcell_build_dir):
        os.makedirs(mcell_build_dir)
    
    # setup cmake build arguments
    cmd_cmake = [opts.cmake_executable]
    cmd_cmake.append(os.path.join(opts.top_dir, REPO_NAME_MCELL))

    cmd_cmake.append(get_cmake_build_type_arg(opts))

    if BUILD_OPTS_USE_LTO:
        cmd_cmake.append('-DUSE_LTO=ON')
        
    # run cmake
    
    # issue (TODO - insert this into the issue tracking system)
    # using gcc-8.3.0 leads to a segfault in nfSim
    if is_default_compiler_supported_by_mcell():
        ec = run(cmd_cmake, mcell_build_dir)
    else:
        log("Not using default gcc 8.3.0 due to unresolved issue, fallback to gcc 7")
        cmd_cmake.insert(0, "CC=gcc-7")
        cmd_cmake.insert(0, "CXX=g++-7")    
        ec = run(cmd_cmake, mcell_build_dir, shell=True)
    check_ec(ec, cmd_cmake)
    
    # setup make build arguments
    cmd_make = ['make']
    cmd_make.append('-j' + str(int(multiprocessing.cpu_count()/2))) 
    
    # run make 
    ec = run(cmd_make, mcell_build_dir, timeout_sec = BUILD_TIMEOUT)
    check_ec(ec, cmd_make)
    
    if 'CYGWIN' in platform.system():
        copy_cygwin_dlls(mcell_build_dir)
    
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
    cmd_cmake = [opts.cmake_executable]
    cmd_cmake.append(os.path.join(opts.top_dir, REPO_NAME_GAMER))
    cmd_cmake.append(get_cmake_build_type_arg(opts))
    cmd_cmake.append('-DCMAKE_INSTALL_PREFIX:PATH=' + gamer_install_dir)
    
    c_flags = ''
    cxx_flags = ''
    if 'CYGWIN' in platform.system():
        flags='-D\'M_PI=3.14159265358979323846\' -D\'M_PI_2=(M_PI/2.0)\' '
        c_flags = c_flags + flags
        cxx_flags = cxx_flags + flags
        
    # library casc requires __has_cpp_attribute c++17 - disable it
    # maybe we can check gcc version and enable it but let's keep it simple for now
    cxx_flags = cxx_flags + '-D\'__has_cpp_attribute(x)=0\''

    # no need to add extra "..." - already handled the way how cmake is run (not as shell)
    cmd_cmake.append('-DCMAKE_C_FLAGS=' + c_flags)
    cmd_cmake.append('-DCMAKE_CXX_FLAGS=' + cxx_flags) 
        
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
    