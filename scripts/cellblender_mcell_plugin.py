"""
Copyright (C) 2019 by
The Salk Institute for Biological Studies and
Pittsburgh Supercomputing Center, Carnegie Mellon University

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
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
    
    cellblender_dir = os.path.join(install_dir, REPO_NAME_CELLBLENDER)
    install_dirs[REPO_NAME_CELLBLENDER] = cellblender_dir  
    
    mcell_dir = os.path.join(cellblender_dir, DIR_EXTENSIONS, REPO_NAME_MCELL)
    install_dirs[REPO_NAME_MCELL] = mcell_dir
    install_dirs[PYTHON_BLENDER_EXECUTABLE] = sys.executable
    return install_dirs 
  
# main entry point  
def create_package(opts) -> None:

    # clear target directory
    plugin_dir = os.path.join(opts.work_dir, CELLBLENDER_MCELL_PLUGIN, REPO_NAME_CELLBLENDER)
    if os.path.exists(plugin_dir):  
        log("Cleaning '" + plugin_dir)
        shutil.rmtree(plugin_dir)
    
    # B) copy cellblender
    log("Installing cellblender to '" + plugin_dir + "'.")
    shutil.copytree(
        os.path.join(opts.work_dir, BUILD_DIR_CELLBLENDER, REPO_NAME_CELLBLENDER),
        plugin_dir,
        symlinks=True
    )
    
    # C) copy mcell
    mcell_dir = os.path.join(plugin_dir, DIR_EXTENSIONS, REPO_NAME_MCELL)
    log("Installing mcell to '" + mcell_dir + "'.")
    shutil.copytree(
        os.path.join(opts.work_dir, BUILD_DIR_MCELL),
        mcell_dir,
        ignore=shutil.ignore_patterns('CMakeFiles', 'deps', '*.a')
    )
    
    # add a version file
    log("Copying version file to '" + plugin_dir + "'.")
    shutil.copy(
        os.path.join(opts.work_dir, RELEASE_INFO_FILE),
        plugin_dir
    )
    
    # sign on MacOS (not sure if this works)
    if platform.system() == 'Darwin' and not opts.do_not_sign_package:
        sign_package_on_macos(plugin_dir)        
        
    # make a package with current date
    top_plugin_dir = os.path.join(opts.work_dir, CELLBLENDER_MCELL_PLUGIN)
    archive_resulting_bundle(opts, top_plugin_dir, REPO_NAME_CELLBLENDER)
    
    # move resulting archive one level up because that's where it is expected
    log("Moving prepared plugin to " + opts.result_bundle_archive_path + ".")
    shutil.move(
        os.path.join(top_plugin_dir, os.path.basename(opts.result_bundle_archive_path)),
        opts.result_bundle_archive_path) 
