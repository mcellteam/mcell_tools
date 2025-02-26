#!/usr/bin/env python3

"""
Copyright (C) 2019,2020 by
The Salk Institute for Biological Studies

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

import os
import platform
from utils import *
from build_settings import *

def get_cmake_build_cmd(opts = None):

    if not opts or not opts.only_pypi_wheel:
        target = 'ALL_BUILD'
    else:
        target = 'mcell4_so'

    # used with MSCV on Windows
    return ['cmake', '--build', '.', '--target', target, '--config', 'Release', '-j', str(get_nr_cores())]


def get_cmake_build_type_arg(opts):
    if opts.debug:
        build_type = 'Debug'
    else:
        build_type = 'Release'

    return '-DCMAKE_BUILD_TYPE=' + build_type


def is_default_compiler_supported_by_mcell() -> bool:
    if platform.system() == 'Linux':
        cmd = ['gcc', '--version']
        res = run_with_ascii_output(cmd, cwd='.')
        if '8.3.0' in res:
            return False
        else:
            # TODO: some error check? maybe we will fix this issue
            return True
    if platform.system() == 'Linux':
        cmd = ['gcc', '--version']
        res = run_with_ascii_output(cmd, cwd='.')
        # just a warning for now
        if res > '8':
            log('Warning: NFsim does not seem to work with gcc version higher or equal to 8...')
        return True
    else:
        # for other OSes let's assume that everything is fine
        return True


def build_mcell(opts):

    if not opts.only_pypi_wheel:
        mcell_build_dir = os.path.join(opts.work_dir, BUILD_DIR_MCELL)
    else:
        mcell_build_dir = os.path.join(opts.work_dir, BUILD_DIR_MCELL_PYPI)

    log("Running mcell build...")

    # create working directory
    if not os.path.exists(mcell_build_dir):
        os.makedirs(mcell_build_dir)

    # setup cmake build arguments
    cmd_cmake = [opts.cmake_executable]
    cmd_cmake += CMAKE_EXTRA_ARGS
    cmd_cmake.append(os.path.join(opts.top_dir, REPO_NAME_MCELL))

    cmd_cmake.append(get_cmake_build_type_arg(opts))

    if BUILD_OPTS_USE_LTO:
        cmd_cmake.append('-DENABLE_LTO=ON')

    if opts.mcell_python:
        # default is 3.11
        cmd_cmake.append('-DPYTHON_VERSION=' + opts.mcell_python)

    if os.name == 'nt':
        # note: may need to rename python39.lib to python3.9 lib on Windows
        cmd_cmake.append('-DSYSTEM_PYTHON_LIB_DIR=' + os.path.join(os.path.dirname(sys.executable), 'libs'))

    # run cmake

    # issue (TODO - insert this into the issue tracking system)
    # using gcc-8.3.0 leads to a segfault in nfSim
    if is_default_compiler_supported_by_mcell():
        ec = run(cmd_cmake, mcell_build_dir)
    else:
        log("Not using default gcc 8.3.0 due to unresolved issue, fallback to gcc 7")
        cmd_cmake.insert(0, "CC=gcc-7")
        cmd_cmake.insert(0, "CXX=g++-7")
        ec = run(cmd_cmake, mcell_build_dir, shell=True)
    check_ec(ec, cmd_cmake)

    if os.name != 'nt':
        # setup make build arguments
        cmd_make = ['make']

        if opts.only_pypi_wheel:
            cmd_make.append('mcell4_so')

        cmd_make.append('-j' + str(get_nr_cores()))

        # run make
        ec = run(cmd_make, mcell_build_dir, timeout_sec = BUILD_TIMEOUT)
        check_ec(ec, cmd_make)
    else:
        # building everything on Windows even whem building just mcell.
        cmd_build = get_cmake_build_cmd(opts)
        ec = run(cmd_build, mcell_build_dir, timeout_sec = BUILD_TIMEOUT)
        check_ec(ec, cmd_build)

    return mcell_build_dir


def build_cellblender(opts):

    cellblender_build_dir = os.path.join(opts.work_dir, BUILD_DIR_CELLBLENDER)
    if opts.clean:
        # TODO
        log("Dry clean of " + cellblender_build_dir)

    # create working directory
    if not os.path.exists(cellblender_build_dir):
        os.makedirs(cellblender_build_dir)

    # setup make build arguments
    # the cellblender installation directory must use unix-style separators
    if 'Windows' in platform.system():
        cellblender_build_dir_unix = cellblender_build_dir.replace('\\', '/')
        cmd_mklink = [ 'mklink', '/J', 'cellblender',  '.' ]
    else:
        cellblender_build_dir_unix = cellblender_build_dir
        cmd_mklink = [ 'ln', '-s', '.',  'cellblender' ]

    # first make a cellblender link directory becaue make creates it only sometimes
    if not os.path.exists(os.path.join(opts.top_dir, REPO_NAME_CELLBLENDER, 'cellblender')):
        ec_mklink = run(cmd_mklink, os.path.join(opts.top_dir, REPO_NAME_CELLBLENDER), shell=True, timeout_sec = BUILD_TIMEOUT)
        check_ec(ec_mklink, cmd_mklink)

    cmd_make = ['make', 'all', '-f', 'makefile', 'install',
         'INSTALL_DIR=' +  cellblender_build_dir_unix ]

    # run make (in-source build)
    ec = run(cmd_make, os.path.join(opts.top_dir, REPO_NAME_CELLBLENDER), timeout_sec = BUILD_TIMEOUT)
    check_ec(ec, cmd_make)

    return os.path.join(cellblender_build_dir, REPO_NAME_CELLBLENDER)


def build_mesh_tools(opts):
    # must be built in source, we would need to rewrite all makefiles otherwise
    mesh_tools_build_dir = os.path.join(opts.top_dir, REPO_NAME_MESH_TOOLS)

    cmd_make = ['make', '-f', 'makefile_neuropil_tools', 'all']

    # run make (in-source build)
    ec = run(cmd_make, os.path.join(opts.top_dir, REPO_NAME_MESH_TOOLS), timeout_sec = BUILD_TIMEOUT)
    check_ec(ec, cmd_make)


def build_vtk(opts):

    vtk_build_dir = os.path.join(opts.work_dir, BUILD_DIR_VTK)

    log("Running VTK build...")

    # create working directory
    if not os.path.exists(vtk_build_dir):
        os.makedirs(vtk_build_dir)

    # setup cmake build arguments
    cmd_cmake = [opts.cmake_executable]
    cmd_cmake += CMAKE_EXTRA_ARGS
    cmd_cmake.append(os.path.join(opts.top_dir, REPO_NAME_VTK))

    # always built as release
    cmd_cmake += [
        '-DCMAKE_BUILD_TYPE=Release',
        '-DVTK_BUILD_TESTING=OFF',
        '-DVTK_BUILD_ALL_MODULES=OFF',
        '-DBUILD_SHARED_LIBS=OFF'
    ]

    # select only the modules that we need
    if True:  # os.name != 'nt':  # it looks like it works on win as well.
        cmd_cmake += [
            '-DVTK_GROUP_ENABLE_Imaging=NO',
            '-DVTK_GROUP_ENABLE_MPI=NO',
            '-DVTK_GROUP_ENABLE_Qt=NO',
            '-DVTK_GROUP_ENABLE_Rendering=NO',
            '-DVTK_GROUP_ENABLE_StandAlone=YES',
            '-DVTK_GROUP_ENABLE_Views=NO',
            '-DVTK_GROUP_ENABLE_Web=NO',
            '-DVTK_MODULE_ENABLE_VTK_RenderingVolumeOpenGL2=NO',
            '-DVTK_MODULE_ENABLE_VTK_IOExport=YES',
            '-DVTK_MODULE_ENABLE_VTK_IOExportGL2PS=NO',
            '-DVTK_MODULE_ENABLE_VTK_RenderingCore=YES',
            '-DVTK_MODULE_ENABLE_VTK_RenderingContext2D=YES',
            '-DVTK_MODULE_ENABLE_VTK_RenderingFreeType=YES',
            '-DVTK_MODULE_ENABLE_VTK_FiltersCore=YES',
            '-DVTK_MODULE_ENABLE_VTK_FiltersGeneral=YES',
            '-DVTK_MODULE_ENABLE_VTK_FiltersPoints=NO'
        ]

    # run cmake
    ec = run(cmd_cmake, vtk_build_dir)
    check_ec(ec, cmd_cmake)

    # run make, will fail
    if os.name != 'nt':
        # setup make build arguments
        cmd_make = ['make']
        cmd_make.append('-j' + str(get_nr_cores()))

        ec = run(cmd_make, vtk_build_dir, timeout_sec = BUILD_TIMEOUT)
    else:
        cmd_build = get_cmake_build_cmd()
        ec = run(cmd_build, vtk_build_dir, timeout_sec = BUILD_TIMEOUT)


def build_all(opts):
    build_dirs = {}

    build_vtk(opts)

    build_dirs[REPO_NAME_MCELL] = build_mcell(opts)

    if not opts.only_pypi_wheel:
        # in-source build for now, should be fixed but it can work like this
        # needed for testing even for 'only_cellblender_mcell'
        build_dirs[REPO_NAME_CELLBLENDER] = build_cellblender(opts)

    if not opts.only_cellblender_mcell and not opts.only_pypi_wheel:
        if 'Windows' not in platform.system():
            build_mesh_tools(opts)

    return build_dirs
