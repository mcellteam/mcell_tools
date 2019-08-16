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

#DEFAULT_BRANCH='development'
# FIXME: use the branch of the mcell_tools repo?
DEFAULT_BRANCH='testing_infrastructure'

WORK_DIR_NAME = 'work'

BUILD_OPTS_USE_LTO = False  # higher performnce but slower build

BUILD_TIMEOUT = 600 # in seconds

REPO_NAME_MCELL = 'mcell'
REPO_NAME_CELLBLENDER = 'cellblender'
REPO_NAME_MCELL_TESTS = 'mcell_tests'

BUILD_DIR_MCELL = 'build_mcell'
BUILD_DIR_CELLBLENDER = 'build_cellblender' # this in fact an install dir for now 

