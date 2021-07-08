"""
Copyright (C) 2019 by
The Salk Institute for Biological Studies and
Pittsburgh Supercomputing Center, Carnegie Mellon University

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

"""
This file contains functions that allow to query cmake version and download
and build a new version if needed.
"""

import os
import re
import multiprocessing

from build_settings import *

CMAKE_LOCAL_INSTALL_DIR = 'cmake_install'
CMAKE_LOCAL_INSTALL_BIN_DIR = os.path.join(CMAKE_LOCAL_INSTALL_DIR, 'bin')
CMAKE_LOCAL_BUILD_DIR = 'cmake_build'

CMAKE_SRC_DIR = 'cmake-3.15.5'
CMAKE_SRC_FILENAME = CMAKE_SRC_DIR + '.tar.gz'
CMAKE_SRC_URL = 'https://github.com/Kitware/CMake/releases/download/v3.15.5/' + CMAKE_SRC_FILENAME 

def check_min_version(major, minor, patch, min_major, min_minor, min_patch):
    if major > min_major:
        return True
    elif major == min_major:
        if  minor > min_minor:
            return True
        elif  minor == min_minor:
            if  patch >= min_patch:
                return True
    return False


# returns pair of bools: able to get version (exists), version sufficien
def get_cmake_info(base_dir: str = '') -> (bool, bool):
    if base_dir:
        cmake_dir = os.path.join(base_dir, CMAKE_SYSTEM_EXECUTABLE)
        if not os.path.exists(cmake_dir):
            return (False, False)
        
    else:
        cmake_dir = CMAKE_SYSTEM_EXECUTABLE
        
    version_str = run_with_ascii_output([cmake_dir, '--version'], cwd=os.getcwd())
    
    # cmake version 
    matches = re.match('cmake version ([0-9]+)\.([0-9]+)\.([0-9]+)', version_str.splitlines()[0])
    
    if matches and len(matches.groups()) == 3:
        major = int(matches.group(1))
        minor = int(matches.group(2))
        patch = int(matches.group(3))
        
        version_ok = check_min_version(major, minor, patch, CMAKE_MIN_MAJOR, CMAKE_MIN_MINOR, CMAKE_MIN_PATCH)
    
        return True, version_ok 
    
    return (False, False)


def download_and_build_cmake(work_dir):
    sources_dir = os.path.join(work_dir, CMAKE_SRC_DIR)
    build_dir = os.path.join(work_dir, CMAKE_LOCAL_BUILD_DIR)
    install_dir = os.path.join(work_dir, CMAKE_LOCAL_INSTALL_DIR)
    
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)
    
    # 1) download
    ec = run(['wget', CMAKE_SRC_URL], cwd=work_dir)
    if ec != 0:
        fatal_error("Could not download cmake sources, cmake of sufficient version must be built manually")
        
    # 2) unzip
    ec = run(TAR_BASE_CMD + ['-xzf', CMAKE_SRC_FILENAME], cwd=work_dir)
    if ec != 0:
        fatal_error("Could extract cmake sources, cmake of sufficient version must be buillt manually")

    # 3) run cmake
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    ec = run(['cmake', sources_dir, '-DCMAKE_INSTALL_PREFIX=' + install_dir], cwd=build_dir)
    if ec != 0:
        fatal_error("Could not run base cmake to build new cmake, cmake of sufficient version must be buillt manually")

    # 3) make install
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    ec = run(['make', 'install', '-j' + str(int(multiprocessing.cpu_count()/2))], cwd=build_dir)
    if ec != 0:
        fatal_error("Could not build cmake, cmake of sufficient version must be buillt manually")
    
    
# returns path to the cmake binary or just 'cmake' if the system version is ok
def build_cmake_if_version_is_insufficient(work_dir) -> str:
    # check the system version first
    exists, version_ok = get_cmake_info()
    
    if exists and version_ok:
        log("System cmake version is sufficient")
        return CMAKE_SYSTEM_EXECUTABLE
    else:
        log("System cmake version is not sufficient")
        # check whether there is a prebuilt 
        prebuilt_dir = os.path.join(work_dir, CMAKE_LOCAL_INSTALL_BIN_DIR) 
        cmake_executable = os.path.join(prebuilt_dir, CMAKE_SYSTEM_EXECUTABLE)
        exists, version_ok = get_cmake_info(prebuilt_dir)
        if exists:
            log("Using prebuilt cmake executable '" + cmake_executable + "'")
            if not version_ok:
                fatal_error("Tried to use cmake in " + prebuilt_dir + " but that version is too old. Clean the local cmake directories")
            return cmake_executable
        else:
            # we need to download the sources and build them
            log("Downloading and building cmake")
            download_and_build_cmake(work_dir)
            log("Built cmake in '" + cmake_executable + "'")
            return cmake_executable 
            
            
    