
"""
Copyright (C) 2021 by
The Salk Institute for Biological Studies and
Pittsburgh Supercomputing Center, Carnegie Mellon University

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
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
    
    