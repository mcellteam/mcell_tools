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

#DEFAULT_BRANCH='development'
# FIXME: use the branch of the mcell_tools repo?
DEFAULT_BRANCH='testing_infrastructure'

WORK_DIR_NAME = 'work'

BUILD_OPTS_USE_LTO = False  # higher performnce but slower build

BUILD_TIMEOUT = 60*30 # in seconds, Windows build can be slow
TEST_ALL_TIMEOUT = 60*60# 1 hour

INTERNAL_RELEASE_NO_VERSION = 'internal'

REPO_NAME_MCELL = 'mcell'
REPO_NAME_CELLBLENDER = 'cellblender'
REPO_NAME_MCELL_TESTS = 'mcell_tests'
REPO_NAME_MCELL_TOOLS = 'mcell_tools'
REPO_NAME_NFSIM = 'nfsim'
REPO_NAME_NFSIMCINTERFACE = 'nfsimCInterface'
REPO_NAME_BIONETGEN = 'bionetgen'
REPO_NAME_GAMER = 'gamer'

BUILD_DIR_MCELL = 'build_mcell'
BUILD_DIR_CELLBLENDER = 'build_cellblender' # this in fact an install dir for now
BUILD_DIR_GAMER = 'build_gamer'
INSTALL_DIR_GAMER = 'install_gamer'

BLENDER_VERSION = '2.79' 
BUILD_DIR_BLENDER = 'blender' #
BUILD_SUBDIR_BLENDER = 'Blender-' + BLENDER_VERSION + '-CellBlender' # name of directory in the resulting arguve

RELEASE_INFO_FILE = 'cellblender_bundle_release_info.txt'

if platform.system() == 'Linux':
    BUILD_SUBDIR_BLENDER_OS_BASED = 'blender-2.79b-linux-glibc219-x86_64'
    BLENDER_ARCHIVE = 'blender-2.79b-linux-glibc219-x86_64.tar.gz'
    MCELL_BUILD_INFRASTRUCTURE_DATA_DIR = '/cnl/mcelldata/mcell_build_infrastructure_data'
elif platform.system() == 'Darwin':
    BUILD_SUBDIR_BLENDER_OS_BASED = 'blender-2.79b-linux-glibc219-x86_64'
    BLENDER_ARCHIVE = 'blender-2.79b-Darwin-18.6.0-x86_64-i386-64bit.tar'
    MCELL_BUILD_INFRASTRUCTURE_DATA_DIR = '/Volumes/mcell/mcell_build_infrastructure_data/'        
elif 'Windows' in platform.system():
    BUILD_SUBDIR_BLENDER_OS_BASED = 'blender-2.79b-windows64'
    BLENDER_ARCHIVE = 'blender-2.79b-windows64.zip'
    MCELL_BUILD_INFRASTRUCTURE_DATA_DIR = 'Z:\\'
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
    TAR_BASE_CMD = ['c:/tools/mingw-w64/x86_64-8.1.0-posix-seh-rt_v6-rev0/mingw64/bin/tar', '--force-local']
    PYTHON_BLENDER_EXECUTABLE = 'python.exe'
    # cmake on Windows tries to use Visual Studio generator by default 
    CMAKE_EXTRA_ARGS = [ '-G', 'Unix Makefiles' ]
else:
    TAR_BASE_CMD = ['tar']
    PYTHON_BLENDER_EXECUTABLE = 'python3.5'
    # keep default generator for cmake 
    CMAKE_EXTRA_ARGS = []

CMAKE_SYSTEM_EXECUTABLE = 'cmake'
CMAKE_MIN_MAJOR = 3
CMAKE_MIN_MINOR = 14
CMAKE_MIN_PATCH = 0

RUN_TESTS_SCRIPT = 'run_tests.py'

MCELL_BUILD_INFRASTRUCTURE_RELEASES_DIR = os.path.join(MCELL_BUILD_INFRASTRUCTURE_DATA_DIR, 'releases')
MCELL_BUILD_INFRASTRUCTURE_BUILDS_DIR = os.path.join(MCELL_BUILD_INFRASTRUCTURE_DATA_DIR, 'builds')
BLENDER_ARCHIVE_DIR = os.path.join(MCELL_BUILD_INFRASTRUCTURE_DATA_DIR, 'blender')
BLENDER_ARCHIVE_LINUX_PATH = os.path.join(BLENDER_ARCHIVE_DIR, BUILD_SUBDIR_BLENDER_OS_BASED + '.tar.bz2')

PYTHON_ARCHIVE_DIR = os.path.join(MCELL_BUILD_INFRASTRUCTURE_DATA_DIR, 'python')
PYTHON_ARCHIVE_PATH = os.path.join(PYTHON_ARCHIVE_DIR, BUILD_SUBDIR_PYTHON + '.tar.xz')

PREBUILT_BLENDER_W_PYTHON_DIR = os.path.join(MCELL_BUILD_INFRASTRUCTURE_DATA_DIR, 'prebuilt_blender_w_python')
PREBUILT_BLENDER_W_PYTHON_EXT = 'tar.gz'

if platform.system() == 'Darwin':
    INSTALL_VERSION_SUBDIR_BLENDER = os.path.join(BUILD_SUBDIR_BLENDER, 'blender.app', 'Contents', 'Resources', BLENDER_VERSION)
else:
    INSTALL_VERSION_SUBDIR_BLENDER = os.path.join(BUILD_SUBDIR_BLENDER, BLENDER_VERSION)


INSTALL_SUBDIR_PYTHON_BIN = os.path.join(INSTALL_VERSION_SUBDIR_BLENDER, BUILD_DIR_PYTHON, BUILD_SUBDIR_BIN_PYTHON_DIR)                    
INSTALL_SUBDIR_CELLBLENDER = os.path.join(INSTALL_VERSION_SUBDIR_BLENDER, 'scripts', 'addons', 'cellblender')
INSTALL_SUBDIR_MCELL = os.path.join(INSTALL_SUBDIR_CELLBLENDER, 'extensions', 'mcell')


BUNDLE_NAME = 'Blender-2.79-CellBlender.' + platform.system()
BUNDLE_EXT = 'tar.gz'

TEST_BUNDLE_DIR = 'bundle_install'


