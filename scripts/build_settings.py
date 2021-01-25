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
This module contains diverse constants used in the checkout and build process.
"""

import os
import platform
import socket
import datetime
from utils import *


DEFAULT_DNS_FOR_SSH_CLONE = [ 'salk.edu' ] 

DEFAULT_BRANCH='master'
DEFAULT_BRANCH_MCELL4='mcell4_dev'
BRANCH_PREFIX_MCELL4='mcell4'

WORK_DIR_NAME = 'work'

BUILD_OPTS_USE_LTO = False  # higher performnce but slower build

BUILD_TIMEOUT = 60*30 # in seconds, Windows build can be slow
TEST_ALL_TIMEOUT = 60*60# 1 hour

INTERNAL_RELEASE_NO_VERSION = 'internal'

REPO_NAME_MCELL = 'mcell'
REPO_NAME_CELLBLENDER = 'cellblender'
REPO_NAME_NEUROPIL_TOOLS = 'neuropil_tools'
REPO_NAME_MESH_TOOLS = 'mesh_tools'

REPO_NAME_MCELL_TESTS = 'mcell_tests'
REPO_NAME_MCELL_TOOLS = 'mcell_tools'
REPO_NAME_NFSIM = 'nfsim'
REPO_NAME_NFSIMCINTERFACE = 'nfsimCInterface'
REPO_NAME_BIONETGEN = 'bionetgen'
REPO_NAME_GAMER = 'gamer'
REPO_NAME_MCELL_TEST_PRIVATE = 'mcell_tests_private'
REPO_NAME_VTK = 'VTK'

BUILD_DIR_MCELL = 'build_mcell'
BUILD_DIR_CELLBLENDER = 'build_cellblender' # this in fact an install dir for now
BUILD_DIR_GAMER = 'build_gamer'
BUILD_DIR_VTK = 'build_vtk'

INSTALL_DIR_GAMER = 'install_gamer'

INSTALL_DIR_MCELL = 'mcell'

BLENDER_VERSION = '2.79'
BLENDER_FULL_VERSION = '2.79b'  
BUILD_DIR_BLENDER = 'blender' #
BUILD_DIR_CELLBLENDER_MCELL = 'cellblender_mcell'
BUILD_SUBDIR_BLENDER = 'Blender-' + BLENDER_VERSION + '-CellBlender' # name of directory in the resulting arguve

RELEASE_INFO_FILE = 'cellblender_bundle_release_info.txt'

if platform.system() == 'Linux':
    BUILD_SUBDIR_BLENDER_OS_BASED = 'blender-2.79b-linux-glibc219-x86_64'
    BLENDER_ARCHIVE = 'blender-2.79b-linux-glibc219-x86_64.tar.gz'
    DEFAULT_MCELL_BUILD_INFRASTRUCTURE_DATA_DIR = '/cnl/mcelldata/mcell_build_infrastructure_data'
    EXE_EXT=""
    BUNDLE_EXT = 'tar.gz'
elif platform.system() == 'Darwin':
    BUILD_SUBDIR_BLENDER_OS_BASED = 'blender-2.79b-linux-glibc219-x86_64'
    BLENDER_ARCHIVE = 'blender-2.79b-Darwin-18.6.0-x86_64-i386-64bit.tar'
    DEFAULT_MCELL_BUILD_INFRASTRUCTURE_DATA_DIR = '/Volumes/mcell/mcell_build_infrastructure_data/'
    EXE_EXT=""
    BUNDLE_EXT = 'zip'        
elif 'Windows' in platform.system():
    BUILD_SUBDIR_BLENDER_OS_BASED = 'blender-2.79b-windows64'
    BLENDER_ARCHIVE = 'blender-2.79b-windows64.zip'
    DEFAULT_MCELL_BUILD_INFRASTRUCTURE_DATA_DIR = 'Z:\\'
    EXE_EXT=".exe"
    BUNDLE_EXT = 'zip'
else:
    fatal_error("Operating system '" + platform.system() + "' is not supported in this build system yet.")

BUILD_SUBDIR_PYTHON_UNDER_BLENDER = os.path.join(BLENDER_VERSION, 'python/')
BUILD_SUBDIR_BIN_PYTHON_DIR = 'bin/python3.5'

BUILD_DIR_PYTHON = 'python'
BUILD_SUBDIR_PYTHON = 'Python-3.5.3'

PYTHON_SYSTEM_EXECUTABLE = 'python3'

if 'Windows' in platform.system():
    # tar interprets colons (:) in file names as meaning it is a file on another machine.
    # TODO: fix this, we really do not want to have an absolute path here but even putting the path into $PATH
    #   somehow did not help 
    #TAR_BASE_CMD = ['c:/tools/mingw-w64/x86_64-8.1.0-posix-seh-rt_v6-rev0/mingw64/bin/tar', '--force-local']
    TAR_BASE_CMD = ['tar.exe'] # used with bsdtar 3.3.2 - libarchive 3.3.2 zlib/1.2.5.f-ipp
    PYTHON_BLENDER_EXECUTABLE = 'python.exe'
    # cmake on Windows uses Visual Studio generator by default 
    CMAKE_EXTRA_ARGS = [] #  '-G', 'Unix Makefiles' 
else:
    TAR_BASE_CMD = ['tar']
    PYTHON_BLENDER_EXECUTABLE = 'python3.5'
    # keep default generator for cmake 
    CMAKE_EXTRA_ARGS = []

ZIP_CMD = ['zip']
UNZIP_CMD = ['unzip']

CMAKE_SYSTEM_EXECUTABLE = 'cmake'
CMAKE_MIN_MAJOR = 3
CMAKE_MIN_MINOR = 14
CMAKE_MIN_PATCH = 0

RUN_TESTS_SCRIPT = 'run_tests.py'

# not really used
BLENDER_ARCHIVE_PATH = os.path.join(DEFAULT_MCELL_BUILD_INFRASTRUCTURE_DATA_DIR, 'blender', BUILD_SUBDIR_BLENDER_OS_BASED + '.tar.bz2')

if platform.system() == 'Darwin':
    INSTALL_VERSION_SUBDIR_BLENDER = os.path.join(BUILD_SUBDIR_BLENDER, 'blender.app', 'Contents', 'Resources', BLENDER_VERSION)
else:
    INSTALL_VERSION_SUBDIR_BLENDER = os.path.join(BUILD_SUBDIR_BLENDER, BLENDER_VERSION)


INSTALL_SUBDIR_PYTHON_BIN = os.path.join(INSTALL_VERSION_SUBDIR_BLENDER, BUILD_DIR_PYTHON, 'bin', PYTHON_BLENDER_EXECUTABLE)                    

INSTALL_SUBDIR_ADDONS = os.path.join(INSTALL_VERSION_SUBDIR_BLENDER, 'scripts', 'addons')
INSTALL_SUBDIR_CELLBLENDER = os.path.join(INSTALL_SUBDIR_ADDONS, 'cellblender')
DIR_EXTENSIONS = 'extensions'
INSTALL_SUBDIR_MCELL = os.path.join(INSTALL_SUBDIR_CELLBLENDER, DIR_EXTENSIONS, 'mcell')
INSTALL_SUBDIR_NEUROPIL_TOOLS = os.path.join(INSTALL_SUBDIR_ADDONS, 'neuropil_tools')

CELLBLENDER_MCELL_PLUGIN = 'cellblender-mcell-plugin'

BUNDLE_NAME = 'Blender-2.79-CellBlender.' + platform.system()

TEST_BUNDLE_DIR = 'bundle_install'



