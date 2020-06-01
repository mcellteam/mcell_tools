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
  Separate script to build blender + python archive.
  
  TODO: just copied code for now, not working yet
  
"""

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
        archive_path = BLENDER_ARCHIVE_PATH
    else:
        fatal_error("Operating system '" + platform.system() + "' is not supported in this build system yet.")
    
    log("Unpacking blender ...")
    cmd = TAR_BASE_CMD + ['-xjf', archive_path, '-C', blender_dir ]
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
    cmd = TAR_BASE_CMD + ['-xf', archive_path, '-C', python_dir ]
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
        cmd = ['./' + PYTHON_BLENDER_EXECUTABLE, '-m', 'pip', 'install', m]
        ec = run(cmd, cwd=os.path.join(blender_python_subdir, 'bin'), timeout_sec=BUILD_TIMEOUT*4, shell=True)
        check_ec(ec, cmd)   


def archive_blender_w_python(opts, blender_dir, prebuilt_archive) -> None:
    # check if the target is accessible
    dir = os.path.dirname(prebuilt_archive)
    if not os.path.exists(dir): 
        warning("Blender archive path '" + dir + "' not found, no archivation of blender with python will be done")
        return
    
    cmd = TAR_BASE_CMD + ['-jcf', prebuilt_archive, BUILD_DIR_BLENDER]
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

if __name__ == "__main__":
    # FIXME: move this to a separate script, python build is quite unreliable 
    # and so far I had to run it several times to finish...
    create_blender_w_python_from_scratch(opts, blender_dir, prebuilt_archive)
