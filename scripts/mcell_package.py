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
import shutil
import sys
import platform
import multiprocessing

from typing import List, Dict

from utils import *
from build_settings import *
from bundle import archive_resulting_bundle, extract_resulting_bundle, get_install_dir


def extract_resulting_package(opts) -> List[str]:
    
    extract_resulting_bundle(opts)
        
    install_dir = get_install_dir(opts) 
    install_dirs = {}
    install_dirs[REPO_NAME_CELLBLENDER] = os.path.join(opts.top_dir, REPO_NAME_CELLBLENDER)  
    install_dirs[REPO_NAME_MCELL] = os.path.join(install_dir, INSTALL_DIR_MCELL)
    install_dirs[PYTHON_BLENDER_EXECUTABLE] = sys.executable
    return install_dirs 
  
# main entry point  
def create_package(opts) -> None:

    # clear target directory
    mcell_dir = os.path.join(opts.work_dir, INSTALL_DIR_MCELL)
    
    if os.path.exists(mcell_dir):  
        log("Cleaning '" + mcell_dir)
        shutil.rmtree(mcell_dir)
    
    log("Installing mcell to '" + mcell_dir + "'.")
    shutil.copytree(
        os.path.join(opts.work_dir, BUILD_DIR_MCELL),
        mcell_dir,
        ignore=shutil.ignore_patterns('CMakeFiles', 'deps', '*.a')
    )
    
    # E) bionetgen
    # NOTE: mcell build already copies all the needed tools, probably that's all we need for now

    # add a version file
    log("Copying version file to '" + mcell_dir + "'.")
    shutil.copy(
        os.path.join(opts.work_dir, RELEASE_INFO_FILE),
        mcell_dir
    )
    
    # sign on MacOS (not sure if this works)
    if platform.system() == 'Darwin' and not opts.do_not_sign_package:
        sign_package_on_macos(mcell_dir)        
        
    # make a package with current date
    archive_resulting_bundle(opts, opts.work_dir, os.path.basename(mcell_dir))
    
