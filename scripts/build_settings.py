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
from utils import *


DEFAULT_DNS_FOR_SSH_CLONE = [ 'salk.edu' ] 

class Options:
    def __init__(self):
        self.update = False
        self.clean = False
        self.ignore_dirty = False
        self.debug = False
        
        self.do_repos = False
        self.do_build = False
        self.do_bundle = False
        self.do_test = False
        
        self.branch = DEFAULT_BRANCH
        
        self.release_version = 'development'
        
        # for developers it might be useful to clone the repositories as ssh
        self.ssh_for_clone = False  
        fqdn = socket.getfqdn()
        for dns in DEFAULT_DNS_FOR_SSH_CLONE:
            if dns in fqdn:
                self.ssh_for_clone = True         
        
        # using os.getcwd() + '..' does not work with links as expected
        self.top_dir = os.path.dirname(get_cwd_no_link())
        self.work_dir = os.path.join(self.top_dir, REPO_NAME_MCELL_TOOLS, WORK_DIR_NAME)

    def __repr__(self):
        attrs = vars(self)
        return ", ".join("%s: %s" % item for item in attrs.items())
            
            
#DEFAULT_BRANCH='development'
# FIXME: use the branch of the mcell_tools repo?
DEFAULT_BRANCH='testing_infrastructure'

WORK_DIR_NAME = 'work'

BUILD_OPTS_USE_LTO = False  # higher performnce but slower build

BUILD_TIMEOUT = 60*10 # in seconds
TEST_ALL_TIMEOUT = 60*60# 1 hour

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
else:
    fatal_error("Operating system '" + platform.system() + "' is not supported in this build system yet.")
 

BUILD_SUBDIR_PYTHON_UNDER_BLENDER = os.path.join(BLENDER_VERSION, 'python/')
BUILD_SUBDIR_BIN_PYTHON_DIR = 'bin/python3.5'

BUILD_DIR_PYTHON = 'python'
BUILD_SUBDIR_PYTHON = 'Python-3.5.3'

PYTHON_SYSTEM_EXECUTABLE = 'python'
PYTHON_BLENDER_EXECUTABLE = './python3.5'

RUN_TESTS_SCRIPT = 'run_tests.py'

# might not be a correct path on Windows
MCELL_BUILD_INFRASTRUCTURE_DATA_DIR = '/cnl/data/mcell_build_infrastructure_data'
BLENDER_ARCHIVE_DIR = os.path.join(MCELL_BUILD_INFRASTRUCTURE_DATA_DIR, 'blender')
BLENDER_ARCHIVE_LINUX_PATH = os.path.join(BLENDER_ARCHIVE_DIR, BUILD_SUBDIR_BLENDER_OS_BASED + '.tar.bz2')

PYTHON_ARCHIVE_DIR = os.path.join(MCELL_BUILD_INFRASTRUCTURE_DATA_DIR, 'python')
PYTHON_ARCHIVE_PATH = os.path.join(PYTHON_ARCHIVE_DIR, BUILD_SUBDIR_PYTHON + '.tar.xz')


PREBUILT_BLENDER_W_PYTHON_DIR = os.path.join(MCELL_BUILD_INFRASTRUCTURE_DATA_DIR, 'prebuilt_blender_w_python')

INSTALL_SUBDIR_CELLBLENDER = os.path.join(BUILD_SUBDIR_BLENDER, BLENDER_VERSION, 'scripts', 'addons', 'cellblender')
INSTALL_SUBDIR_MCELL = os.path.join(INSTALL_SUBDIR_CELLBLENDER, 'extensions', 'mcell')

BUNDLE_NAME = 'Blender-2.79-CellBlender.' + platform.system()
BUNDLE_EXT = 'tar.gz'

TEST_BUNDLE_DIR = 'bundle_install'

