
"""
Copyright (C) 2021 by
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

from utils import *
from build_settings import *
import sys
import platform
import shutil

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

PYPI_WORK_DIR = 'build_pypi_wheel'
DIST_DIR = 'dist'

def create_pypi_wheel(opts):
    os.chdir(opts.work_dir)
    
    if os.path.exists(PYPI_WORK_DIR):
        log("Cleaning '" + PYPI_WORK_DIR + "'")
        shutil.rmtree(PYPI_WORK_DIR)
    os.mkdir(PYPI_WORK_DIR)
    os.chdir(PYPI_WORK_DIR)
    
    # there is no official list for the platform names...
    if platform.system() == 'Linux':
        platform_arg = 'manylinux1_x86_64'
        lib_ext = '.so'
        lib_name = 'mcell.cpython-35m-x86_64-linux-gnu.so'
    elif platform.system() == 'Darwin':
        lib_ext = '.so'
        platform_arg = 'macosx' # probably wrong
        lib_name = 'mcell.cpython-35m-x86_64-darwin.so'
    elif 'Windows' in platform.system():
        lib_ext = '.pyd'
        lib_name = 'mcell.cpython-35m-x86_64-win32.so'
        platform_arg = 'win64' # probably wrong
    
    # copy MCell library and set correct name
    lib_dir = os.path.join('build', 'lib')
    os.makedirs(lib_dir)
    shutil.copy(
        os.path.join(opts.work_dir, BUILD_DIR_MCELL_PYPI, 'lib', 'mcell' + lib_ext),
        os.path.join(lib_dir, lib_name)
    )
    
    
    cmd = [
        sys.executable, 
        os.path.join(THIS_DIR, '..', 'pypi_wheel', 'setup.py'),
        'bdist_wheel',
        '-p', platform_arg
    ]
    
    ec = run(cmd, timeout_sec = BUILD_TIMEOUT, cwd=os.getcwd())
    check_ec(ec, cmd)
    
    # TODO: check the size of the resulting whl file
    
    