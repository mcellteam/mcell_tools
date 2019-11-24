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
This file contains functions that allow to query cmake version and download
and build a new version if needed.
"""

import os
import re

import build_settings

# returns pair of bools: able to get version (exists), version sufficien
def get_cmake_info(base_path: str = '') -> bool, bool:
    if base_path:
        cmake_path = os.path.join(base_path, CMAKE_SYSTEM_EXECUTABLE)
    else:
        cmake_path = CMAKE_SYSTEM_EXECUTABLE
        
    version_str = run_with_ascii_output([cmake_path, '--version'])
    
    matches = re.match('cmake version (\d+)\.(\d+)\.\(d+.)*', version_str)
    
    if matches and len(matches.group) == 3:
        major = int(matches.group(1))
        minor = int(matches.group(2))
        patch = int(matches.group(3))
        
        version_ok = check_min_version(major, minor, patch, CMAKE_MIN_MAJOR, CMAKE_MIN_MINOR, CMAKE_MIN_PATCH)
    
        return True, version_ok 
    
    return False, False
    
    
# returns path to the cmake binary or just 'cmake' if the system version is ok
def build_cmake_if_version_is_insufficient(work_dir) -> str:
    # check the system version first
    exists, version_ok = get_cmake_info()
    
    if exists and version_ok:
        log("System cmake version is sufficient")
        return CMAKE_SYSTEM_EXECUTABLE
    else:
        # check whether there is a prebuilt 
        prebuilt_path = os.path.join(work_dir, CMAKE_LOCAL_INSTALL_BIN_DIR) 
        exists, version_ok = get_cmake_info(prebuilt_path)
        if exists:
            if not version_ok:
                fatal_error("Tried to use cmake in " + prebuilt_path + " but that version is too old. Clean the local cmake directories")
                
            return os.path.join(prebuilt_path, CMAKE_SYSTEM_EXECUTABLE)
        else:
            # we need to download the sources and build them
            fatal_error("TODO: donwload and build")
            
            
    