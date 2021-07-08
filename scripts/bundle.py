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
from build import get_cmake_build_cmd

def copy_prebuilt_blender_w_python(opts) -> None:
    log("Copying pre-built blender with python from '" + opts.prebuilt_blender_w_python_base + "'.") 
    if not os.path.exists(opts.prebuilt_blender_w_python_base):
        fatal_error("Could not find prebuilt blender + python package " + opts.prebuilt_blender_w_python_base)
        
    recursive_overwrite(opts.prebuilt_blender_w_python_base, opts.work_dir) 
        
        
def copy_override_files(opts) -> None:        
    log("Copying pre-built override files from '" + opts.prebuilt_blender_w_python_override + "'.")
    if not os.path.exists(opts.prebuilt_blender_w_python_override):
        fatal_error("Could not find prebuilt blender + python package " + opts.prebuilt_blender_w_python_override)
        
    recursive_overwrite(opts.prebuilt_blender_w_python_override, opts.work_dir) 


def sign_package_on_macos(blender_dir) -> None:
    log("Signing MacOS package in '" + blender_dir + "'.")
    
    blender279_dir = os.path.join(blender_dir, BUILD_SUBDIR_BLENDER)
    
    # need to pack and unpack it first with tar gfor some reason otherwise codesign prints
    # "unsealed contents present in the bundle root"
    tar_cmd = TAR_BASE_CMD + ['-zcf', 'tmp.tar.gz', BUILD_SUBDIR_BLENDER]
    ec = run(tar_cmd, cwd=blender_dir, timeout_sec=BUILD_TIMEOUT)
    shutil.rmtree(blender279_dir)

    untar_cmd = TAR_BASE_CMD + ['-xzf', 'tmp.tar.gz']
    ec = run(untar_cmd, cwd=blender_dir, timeout_sec=BUILD_TIMEOUT)

    # then we can sign it     
    cmd = [
        'codesign', '--verbose', '--deep', '--force', 
        '--sign', '"Developer ID Application: Adam Husar (342MS8AP75)"',
        os.path.join(blender279_dir, 'blender.app')
    ]
    
    # must be run from work_dir to avoid having full paths in the archive
    ec = run(cmd, shell=True, cwd=blender_dir, timeout_sec=BUILD_TIMEOUT)
    check_ec(ec, cmd)  
    

def archive_resulting_bundle(opts, blender_dir, dir_to_archive=BUILD_SUBDIR_BLENDER) -> None:
    log("Creating resulting archive '" + opts.result_bundle_archive_path + "'.")
    
    if platform.system() == 'Linux':
        cmd = TAR_BASE_CMD + ['-zcf', os.path.basename(opts.result_bundle_archive_path), dir_to_archive]
    else:
        cmd = ZIP_CMD + ['-r', os.path.basename(opts.result_bundle_archive_path), dir_to_archive]
        
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
    
    if os.name != 'nt':
        # setup make build arguments
        cmd_make = ['make']
        cmd_make.append('-j' + str(get_nr_cores())) 
        
        # run make 
        ec = run(cmd_make, gamer_build_dir, timeout_sec = BUILD_TIMEOUT)
        check_ec(ec, cmd_make)
    else:
        cmd_build = get_cmake_build_cmd()
        ec = run(cmd_build, gamer_build_dir, timeout_sec = BUILD_TIMEOUT)


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
        ignore=shutil.ignore_patterns('CMakeFiles', 'deps', '*.a', '*.tlog', '*.log', '*.dir')
    )
    
    # neuropil_tools and mesh_tools 
    if 'Windows' not in platform.system():
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
    
    # add additional system-specific files
    copy_override_files(opts)
    
    # sign on MacOS
    if platform.system() == 'Darwin' and not opts.do_not_sign_package:
        sign_package_on_macos(blender_dir)        
        
    # make a package with current date
    archive_resulting_bundle(opts, blender_dir)
    
