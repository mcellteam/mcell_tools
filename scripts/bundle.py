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


def unpack_prebuilt_blender_w_python(opts, prebuilt_archive) -> None:
    log("Using pre-built variant of blender with python...")

    # simply extract the prebuilt archive, 
    # the archive already has atop directory called 'blender' 
    cmd = TAR_BASE_CMD + ['-xf', prebuilt_archive, '-C', opts.work_dir ]
    ec = run(cmd, timeout_sec=BUILD_TIMEOUT)
    check_ec(ec, cmd)


def archive_resulting_bundle(opts, blender_dir) -> None:
    log("Creating resulting archive '" + opts.result_bundle_archive_path + "'.")
    # TODO: better versioning, e.g. from argument
    cmd = TAR_BASE_CMD + ['-zcf', os.path.basename(opts.result_bundle_archive_path), BUILD_SUBDIR_BLENDER]
    # must be run from work_dir to avoid having full paths in the archive
    ec = run(cmd, cwd=blender_dir, timeout_sec=BUILD_TIMEOUT)
    check_ec(ec, cmd)  


def unpack_gamer(opts, blender_dir):
    # not sure which version will be make, expecting that there will be just one .zip file
    # in the build_gamer dir
    build_gamer_dir = os.path.join(opts.work_dir, BUILD_DIR_GAMER)
    blendgamer_zip = ''
    
    for file in os.listdir(build_gamer_dir):
        if file.startswith('blendgamer') and file.endswith(".zip"):
            if blendgamer_zip:
                fatal_error('Found multiple blendgamer zip files in ' + build_gamer_dir + '.')
            blendgamer_zip = file
            
    if not blendgamer_zip:
        fatal_error('Did not find blendgamer zip file in ' + build_gamer_dir + '.')
        
    addons_dir = os.path.join(blender_dir, INSTALL_SUBDIR_ADDONS)
    
    # unpack it 
    cmd = UNZIP_CMD + [blendgamer_zip, '-d', addons_dir]
    # must be run from work_dir to avoid having full paths in the archive
    ec = run(cmd, cwd=build_gamer_dir, timeout_sec=BUILD_TIMEOUT)
    check_ec(ec, cmd)  
    

def get_install_dir(opts) -> str:
    return os.path.join(opts.work_dir, TEST_BUNDLE_DIR)


def get_extracted_bundle_install_dirs(opts) -> List[str]:    
    install_dir = get_install_dir(opts) 
    install_dirs = {}
    install_dirs[REPO_NAME_CELLBLENDER] = os.path.join(install_dir, INSTALL_SUBDIR_CELLBLENDER)  
    install_dirs[REPO_NAME_MCELL] = os.path.join(install_dir, INSTALL_SUBDIR_MCELL)
    # TODO: cannot run python on MacOS without being installed under Applciations, 
    # need to fix this
    if platform.system() != 'Darwin':
        install_dirs[PYTHON_BLENDER_EXECUTABLE] = os.path.join(install_dir, INSTALL_SUBDIR_PYTHON_BIN)
    return install_dirs 
    
# called from run.py when testing is enabled
# returns directory that points to locations where cellblender and 
# mcell are installed
def extract_resulting_bundle(opts) -> List[str]:
        
    install_dir = get_install_dir(opts)
                 
    if os.path.exists(install_dir):  
        log("Cleaning '" + install_dir)
        shutil.rmtree(install_dir)
    os.makedirs(install_dir)
            
    log("Unpacking resulting archive for testing '" + opts.result_bundle_archive_path + "'.")
    # TODO: better versioning, e.g. from argument
    # TODO: make a function for tar calls
    cmd = TAR_BASE_CMD + ['-xzf', opts.result_bundle_archive_path]
    
    ec = run(cmd, cwd=install_dir, timeout_sec=BUILD_TIMEOUT)
    check_ec(ec, cmd)  
    
    return get_extracted_bundle_install_dirs(opts)
  
  
# main entry point  
def create_bundle(opts) -> None: 
    # is there a pre-built version? - building Python takes long time 

    # clear target directory
    blender_dir = os.path.join(opts.work_dir, BUILD_DIR_BLENDER)
    
    if os.path.exists(blender_dir):  
        log("Cleaning '" + blender_dir)
        shutil.rmtree(blender_dir)
    
    # A) prepare blender directory with new python
    prebuilt_archive = opts.prebuilt_blender_w_python_archive    
    log("Checking for pre-built blender with python at '" + prebuilt_archive + "'.") 
    if os.path.exists(prebuilt_archive):
        unpack_prebuilt_blender_w_python(opts, prebuilt_archive)
    else:
        fatal_error("Could not find prebuilt blender + python package " + prebuilt_archive)
    
    # B) copy cellblender
    cellblender_dir = os.path.join(blender_dir, INSTALL_SUBDIR_CELLBLENDER)
    log("Installing cellblender to '" + cellblender_dir + "'.")
    shutil.copytree(
        os.path.join(os.path.join(opts.work_dir), BUILD_DIR_CELLBLENDER, REPO_NAME_CELLBLENDER),
        cellblender_dir,
        symlinks=True
    )
    
    # C) copy mcell
    mcell_dir = os.path.join(blender_dir, INSTALL_SUBDIR_MCELL)
    log("Installing mcell to '" + mcell_dir + "'.")
    shutil.copytree(
        os.path.join(opts.work_dir, BUILD_DIR_MCELL),
        mcell_dir
    )
    
    
    # D) other dependencies that might be needed
    if platform.system() == 'Darwin':
        shutil.copyfile(
            os.path.join(opts.top_dir, REPO_NAME_MCELL_TOOLS, 'system_libs', 'darwin', 'libintl.8.dylib'),
            os.path.join(mcell_dir, 'lib', 'libintl.8.dylib')
        )
            
    # D) gamer
    if not opts.do_not_build_gamer:
        unpack_gamer(opts, blender_dir)
    
    # E) bionetgen
    # NOTE: mcell build already copies all the needed tools, probably that's all we need for now
    
    # add a version file
    blender_subdir = os.path.join(blender_dir, BUILD_SUBDIR_BLENDER)
    log("Copying version file to '" + blender_subdir + "'.")
    shutil.copy(
        os.path.join(opts.work_dir, RELEASE_INFO_FILE),
        blender_subdir
    )
    
    # make a package with current date
    archive_resulting_bundle(opts, blender_dir)
    
