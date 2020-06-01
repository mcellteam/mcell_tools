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

def copy_prebuilt_blender_w_python(opts) -> None:
    log("Copying pre-built blender with python from '" + opts.prebuilt_blender_w_python_base + "'.") 
    if not os.path.exists(opts.prebuilt_blender_w_python_base):
        fatal_error("Could not find prebuilt blender + python package " + opts.prebuilt_blender_w_python_base)
        
    recursive_overwrite(opts.prebuilt_blender_w_python_base, opts.work_dir) 
        
    # Linux build also needs an override directory
    if platform.system() == 'Linux':
        if not os.path.exists(opts.prebuilt_blender_w_python_override):
            fatal_error("Could not find prebuilt blender + python package " + opts.prebuilt_blender_w_python_override)
            
        recursive_overwrite(opts.prebuilt_blender_w_python_override, opts.work_dir) 


def sign_package_on_macos(blender_dir) -> None:
    log("Signing MacOS package in '" + blender_dir + "'.")
     
    cmd = [
        'codesign', '--verbose', '--deep', '--force', 
        '--sign', '"3rd Party Mac Developer Application: Adam Husar (342MS8AP75)"',
        os.path.join(blender_dir, BUILD_SUBDIR_BLENDER, 'blender.app')
    ]
    
    # must be run from work_dir to avoid having full paths in the archive
    ec = run(cmd, cwd=blender_dir, timeout_sec=BUILD_TIMEOUT)
    check_ec(ec, cmd)  
    

def archive_resulting_bundle(opts, blender_dir) -> None:
    log("Creating resulting archive '" + opts.result_bundle_archive_path + "'.")
    
    if platform.system() == 'Linux':
        cmd = TAR_BASE_CMD + ['-zcf', os.path.basename(opts.result_bundle_archive_path), BUILD_SUBDIR_BLENDER]
    else:
        cmd = ZIP_CMD + ['-r', os.path.basename(opts.result_bundle_archive_path), BUILD_SUBDIR_BLENDER]
        
    # must be run from work_dir to avoid having full paths in the archive
    ec = run(cmd, cwd=blender_dir, timeout_sec=BUILD_TIMEOUT)
    check_ec(ec, cmd)  


def build_gamer(opts, blender_dir):
    log("Running gamer build...")

    cmake_blendgamer_script = os.path.join(opts.top_dir, 'mcell_tools', 'scripts', 'cmake_blendgamer.sh')
    gamer_build_dir = os.path.join(opts.work_dir, BUILD_DIR_GAMER)
    
    if not os.path.exists(gamer_build_dir):  
        os.makedirs(gamer_build_dir)
    
    cmd_bash_cmake = ['bash', cmake_blendgamer_script, blender_dir, gamer_build_dir]
    
    # run cmake
    ec = run(cmd_bash_cmake, gamer_build_dir, timeout_sec = BUILD_TIMEOUT)
    check_ec(ec, cmd_bash_cmake)
    
    # setup make build arguments
    cmd_make = ['make']
    cmd_make.append('-j' + str(get_nr_cores())) 
    
    # run make 
    ec = run(cmd_make, gamer_build_dir, timeout_sec = BUILD_TIMEOUT)
    check_ec(ec, cmd_make)


def unpack_blendgamer(opts, blender_dir):
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
    

def install_neuropil_tools(opts, neuropil_tools_dir):
    if os.path.exists(neuropil_tools_dir):  
        log("Cleaning '" + neuropil_tools_dir)
        shutil.rmtree(neuropil_tools_dir)
    os.makedirs(neuropil_tools_dir)
    
    log("Installing mesh_tools to '" + neuropil_tools_dir + "'.")
    # first install binaries and scripts from mesh_tools
    cmd_make_install = ['make', '-f', 'makefile_neuropil_tools', 'install', 'INSTALL_DIR='+os.path.join(neuropil_tools_dir, 'bin'), 'EXE='+EXE_EXT]
    ec = run(cmd_make_install, os.path.join(opts.top_dir, REPO_NAME_MESH_TOOLS), timeout_sec = BUILD_TIMEOUT)
    check_ec(ec, cmd_make_install)
    
    # then copy all *.py files from neuropil_tools
    log("Installing neuropil_tools to '" + neuropil_tools_dir + "'.")
    neuropil_tools_repo_dir = os.path.join(opts.top_dir, REPO_NAME_NEUROPIL_TOOLS)
    for basename in os.listdir(neuropil_tools_repo_dir):
        if basename.endswith('.py'):
            pathname = os.path.join(neuropil_tools_repo_dir, basename)
            if os.path.isfile(pathname):
                shutil.copy2(pathname, neuropil_tools_dir)
    

def get_install_dir(opts) -> str:
    return os.path.join(opts.work_dir, TEST_BUNDLE_DIR)


def get_extracted_bundle_install_dirs(opts) -> List[str]:    
    install_dir = get_install_dir(opts) 
    install_dirs = {}
    install_dirs[REPO_NAME_CELLBLENDER] = os.path.join(install_dir, INSTALL_SUBDIR_CELLBLENDER)  
    install_dirs[REPO_NAME_MCELL] = os.path.join(install_dir, INSTALL_SUBDIR_MCELL)
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
    
    if platform.system() == 'Linux':
        cmd = TAR_BASE_CMD + ['-xzf', opts.result_bundle_archive_path]
    else:
        cmd = UNZIP_CMD + [opts.result_bundle_archive_path]
    
    ec = run(cmd, cwd=install_dir, timeout_sec=BUILD_TIMEOUT)
    check_ec(ec, cmd)  
    
    return get_extracted_bundle_install_dirs(opts)

  
# main entry point  
def create_bundle(opts) -> None:

    # clear target directory
    blender_dir = os.path.join(opts.work_dir, BUILD_DIR_BLENDER)
    
    if os.path.exists(blender_dir):  
        log("Cleaning '" + blender_dir)
        shutil.rmtree(blender_dir)
    
    # A) prepare blender directory with new python
    copy_prebuilt_blender_w_python(opts)
    
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
        mcell_dir,
        ignore=shutil.ignore_patterns('CMakeFiles', 'deps', '*.a')
    )
    
    # neuropil_tools and mesh_tools 
    neuropil_tools_dir = os.path.join(blender_dir, INSTALL_SUBDIR_NEUROPIL_TOOLS)
    install_neuropil_tools(opts, neuropil_tools_dir)
        
    # gamer
    if not opts.do_not_build_gamer:
        # gamer must be built at this phase because we need the blender executable
        build_gamer(opts, blender_dir)
        unpack_blendgamer(opts, blender_dir)
    
    # E) bionetgen
    # NOTE: mcell build already copies all the needed tools, probably that's all we need for now
    
    # other dependencies that might be needed and must be installed after plugins 
    if platform.system() == 'Darwin':
        shutil.copyfile(
            os.path.join(opts.top_dir, REPO_NAME_MCELL_TOOLS, 'system_files', 'darwin', 'libintl.8.dylib'),
            os.path.join(mcell_dir, 'lib', 'libintl.8.dylib')
        )
    
    # add a version file
    blender_subdir = os.path.join(blender_dir, BUILD_SUBDIR_BLENDER)
    log("Copying version file to '" + blender_subdir + "'.")
    shutil.copy(
        os.path.join(opts.work_dir, RELEASE_INFO_FILE),
        blender_subdir
    )
    
    # sign on MacOS
    if platform.system() == 'Darwin':
        sign_package_on_macos(blender_dir)        
        
    # make a package with current date
    archive_resulting_bundle(opts, blender_dir)
    
