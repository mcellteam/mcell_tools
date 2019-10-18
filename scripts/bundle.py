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


AUTOMATICALLY_ARCHIVE_BLENDER_W_PYTHON = True

MODULES_TO_INSTALL = [
    'pybind11',
    'requests',
    'numpy',
    'scipy',
    'matplotlib',
    'PyDSTool',
    'lxml',
    'pyyaml',
    'MeshPy',
    'python-libsbml'
]


def unpack_blender(opts, blender_dir) -> None:
    if platform.system() == 'Linux':
        archive_path = BLENDER_ARCHIVE_LINUX_PATH
    else:
        fatal_error("Operating system '" + platform.system() + "' is not supported in this build system yet.")
    
    log("Unpacking blender ...")
    cmd = ['tar', '-xjf', archive_path, '-C', blender_dir ]
    ec = run(cmd)
    check_ec(ec, cmd)

    log("Renaming blender subdir from '" + BUILD_SUBDIR_BLENDER_OS_BASED + "' to '" + BUILD_SUBDIR_BLENDER + "'.")
    os.rename(
        os.path.join(blender_dir, BUILD_SUBDIR_BLENDER_OS_BASED), 
        os.path.join(blender_dir, BUILD_SUBDIR_BLENDER))


def unpack_python(opts, python_dir) -> None:
    archive_path = PYTHON_ARCHIVE_PATH

    # clear target directory
    if os.path.exists(python_dir):
        log("Cleaning '" + python_dir)
        shutil.rmtree(python_dir)
    os.makedirs(python_dir)
    
    log("Unpacking python sources ...")
    cmd = ['tar', '-xf', archive_path, '-C', python_dir ]
    ec = run(cmd)
    check_ec(ec, cmd)


def print_python_gcc_message(python_subdir) -> None: 
    log("Python build might fail with gcc 4.9.2, see https://stackoverflow.com/questions/46279671/compile-python-3-6-2-on-debian-jessie-segfaults-on-sharedmods")
    log("Try to run 'make' and 'make install' in '" + python_subdir + "' manually.") 


def build_python(opts, python_dir, blender_python_subdir) -> None:
    #archive_path = PYTHON_ARCHIVE_PATH
    
    # TODO: consider having pre-built python, however, different Linux OSes...
    log("Building python sources ...")
    
    # there should be a single subdirectory for now fixed name is expected 
    # e.g. .../mcell_tools/work/blender/blender-2.79b-linux-glibc219-x86_64/2.79/python 
    python_subdir = os.path.join(python_dir, BUILD_SUBDIR_PYTHON)
    
    cmd_configure = ['bash', './configure', '--enable-optimizations', '--prefix=' + blender_python_subdir]
    ec = run(cmd_configure, cwd=python_subdir)
    check_ec(ec, cmd_configure)

    parallel_arg = '-j' + str(int(multiprocessing.cpu_count()/2))

    cmd_make = ['make', parallel_arg]
    # fails when shell=False, might take long time to build
    ec = run(cmd_make, cwd=python_subdir, timeout_sec=BUILD_TIMEOUT*10, shell=True)
    if ec != 0:
        print_python_gcc_message(python_subdir)
    check_ec(ec, cmd_make)

    # running make install does not install everything correctly
    cmd_make_install = ['make', 'install', parallel_arg]
    # fails when shell=False, might take long time to build
    ec = run(cmd_make_install, cwd=python_subdir, timeout_sec=BUILD_TIMEOUT*10, shell=True)
    if ec != 0:
        print_python_gcc_message(python_subdir)
    check_ec(ec, cmd_make_install)


def install_python_packages(opts, blender_python_subdir) -> None:
    for m in MODULES_TO_INSTALL:
        # Running ./pip3 install MeshPy fails with missing include, we need to run pip through python
        cmd = [PYTHON_BLENDER_EXECUTABLE, '-m', 'pip', 'install', m]
        ec = run(cmd, cwd=os.path.join(blender_python_subdir, 'bin'), timeout_sec=BUILD_TIMEOUT*4, shell=True)
        check_ec(ec, cmd)   


def archive_blender_w_python(opts, blender_dir, prebuilt_archive) -> None:
    # check if the target is accessible
    dir = os.path.dirname(prebuilt_archive)
    if not os.path.exists(dir): 
        warning("Blender archive path '" + dir + "' not found, no archivation of blender with python will be done")
        return
    
    cmd = ['tar', '-jcf', prebuilt_archive, BUILD_DIR_BLENDER]
    # must be run from work_dir to avoid having full paths in the archive
    ec = run(cmd, cwd=opts.work_dir, timeout_sec=BUILD_TIMEOUT)
    check_ec(ec, cmd)   
    

def create_blender_w_python_from_scratch(opts, blender_dir, prebuilt_archive) -> None:
    
    if not os.path.exists(blender_dir):
        os.makedirs(blender_dir)

    # 1)
    unpack_blender(opts, blender_dir)
    
    # 2)
    python_dir = os.path.join(opts.work_dir, BUILD_DIR_PYTHON)
    unpack_python(opts, python_dir)
    
    # TODO: needed for MAC OS
    # build_python_prerequisites(opts, python_dir)
    
    blender_python_subdir = os.path.join(
        opts.work_dir, BUILD_DIR_BLENDER, 
        BUILD_SUBDIR_BLENDER, BUILD_SUBDIR_PYTHON_UNDER_BLENDER)
    build_python(opts, python_dir, blender_python_subdir)
    
    #3)
    install_python_packages(opts, blender_python_subdir) 
    
    # create archive for later usage
    archive_blender_w_python(opts, blender_dir, prebuilt_archive)


def unpack_prebuilt_blender_w_python(opts, prebuilt_archive) -> None:
    log("Using pre-built variant of blender with python...")

    # simply extract the prebuilt archive, 
    # the archive already has atop directory called 'blender' 
    cmd = ['tar', '-xjf', prebuilt_archive, '-C', opts.work_dir ]
    ec = run(cmd, timeout_sec=BUILD_TIMEOUT)
    check_ec(ec, cmd)


def archive_resulting_bundle(opts, blender_dir) -> None:
    log("Creating resulting archive '" + opts.result_bundle_archive_path + "'.")
    # TODO: better versioning, e.g. from argument
    cmd = ['tar', '-zcf', os.path.basename(opts.result_bundle_archive_path), BUILD_SUBDIR_BLENDER]
    # must be run from work_dir to avoid having full paths in the archive
    ec = run(cmd, cwd=blender_dir, timeout_sec=BUILD_TIMEOUT)
    check_ec(ec, cmd)  

def get_install_dir(opts) -> str:
    return os.path.join(opts.work_dir, TEST_BUNDLE_DIR)


def get_extracted_bundle_install_dirs(opts) -> List[str]:    
    install_dir = get_install_dir(opts) 
    install_dirs = {}
    install_dirs[REPO_NAME_CELLBLENDER] = os.path.join(install_dir, INSTALL_SUBDIR_CELLBLENDER)  
    install_dirs[REPO_NAME_MCELL] = os.path.join(install_dir, INSTALL_SUBDIR_MCELL)
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
    cmd = ['tar', '-xzf', opts.result_bundle_archive_path]
    
    ec = run(cmd, cwd=install_dir, timeout_sec=BUILD_TIMEOUT)
    check_ec(ec, cmd)  
    
    return get_extracted_bundle_install_dirs(opts)
  
# main entry point  
def create_bundle(opts) -> None: 
    # is there a pre-built version? - building Python takes long time 
    versions_info = BUILD_SUBDIR_BLENDER_OS_BASED + '-' + BUILD_SUBDIR_PYTHON + '-' + platform.system() + '-' + platform.release()
    prebuilt_archive = os.path.join(PREBUILT_BLENDER_W_PYTHON_DIR, versions_info) + '.tar.bz2'

    # clear target directory
    blender_dir = os.path.join(opts.work_dir, BUILD_DIR_BLENDER)
    
    if os.path.exists(blender_dir):  
        log("Cleaning '" + blender_dir)
        shutil.rmtree(blender_dir)
    
    # A) prepare blender directory with new python    
    log("Checking for pre-built blender with python at '" + prebuilt_archive + "'.") 
    if os.path.exists(prebuilt_archive):
        unpack_prebuilt_blender_w_python(opts, prebuilt_archive)
    else:
        # FIXME: move this to a separate script, python build is quite unreliable 
        # and so far I had to run it several times to finish...
        create_blender_w_python_from_scratch(opts, blender_dir, prebuilt_archive)
    
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
        os.path.join(os.path.join(opts.work_dir), BUILD_DIR_MCELL),
        mcell_dir
    )
    
    # D) gamer
    # TODO - not sure what to include
    
    # E) bionetgen
    # TODO - not sure what to include
    
    # add a version file
    blender_subdir = os.path.join(blender_dir, BUILD_SUBDIR_BLENDER)
    log("Copying version file to '" + blender_subdir + "'.")
    shutil.copy(
        os.path.join(opts.work_dir, RELEASE_INFO_FILE),
        blender_subdir
    )
    
    # make a package with current date
    archive_resulting_bundle(opts, blender_dir)
    