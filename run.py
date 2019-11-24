#!/usr/bin/env python3

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
import sys
import subprocess


THIS_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(THIS_DIR, 'scripts'))

# TODO: simplify calls to os.path.join? 
import repositories
import build
import bundle
import cmake_builder

from utils import log, fatal_error, get_cwd_no_link
from build_settings import *
from options import Options


def check_prerequisites(opts):
    if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 5):
        # this is what cellblender was using, not sure, maybe just version 3.* suffices 
        fatal_error("Required Python version is at least 3.5")
        
        
    # also check cmake (although it is not needed for all task types)
    opts.cmake_path = cmake_builder.build_cmake_if_version_is_insufficient(opts.work_dir)
    
    
def test_all(opts, install_dirs):    
    # check if there is an extracted bundle already
    if not install_dirs:
        install_dirs = bundle.get_extracted_bundle_install_dirs(opts)

    # running testting as a new process
    tests_path = os.path.join(THIS_DIR, '..', REPO_NAME_MCELL_TESTS)
    test_cmd = [
        PYTHON_SYSTEM_EXECUTABLE, 
        os.path.join(tests_path, RUN_TESTS_SCRIPT)
    ]
    if REPO_NAME_MCELL in install_dirs:
        test_cmd += [ '-m', install_dirs[REPO_NAME_MCELL] ]

    if REPO_NAME_CELLBLENDER in install_dirs:
        test_cmd += [ '-b', install_dirs[REPO_NAME_CELLBLENDER] ]
        
    # for some reason the script dos not terminate without the shell=True
    ec = run(test_cmd, timeout_sec=TEST_ALL_TIMEOUT, cwd=tests_path, shell=True)
    if ec != 0:
        fatal_error("Testing failed")


def main():
    opts = Options()
    opts.process_opts()
    print(opts)
    
    check_prerequisites()

    return

    log("Top directory: " + opts.top_dir)

    #
    if opts.print_platform_info:
        print("Required blender + python archive name:")
        print(opts.prebuilt_blender_w_python_archive)
        
        print("Resulting bundle name:")
        print(opts.result_bundle_archive_path)
        return


    # clean
    if opts.clean:
        if os.path.exists(opts.work_dir):
            log("Cleaning '" + opts.work_dir + "'")
            shutil.rmtree(opts.work_dir)
        else:
            log("Nothing to clean in '" + opts.work_dir + "'")
        sys.exit(0)
 

    # 1) get all the sources
    if opts.do_repos:
        repositories.get_or_update(opts)
    
    # 2) build
    # returns dictionary  repo name -> where it was built
    if opts.do_build:
        # generate version file 
        repositories.create_version_file(opts)
        
        # keys are REPO_NAME_MCELL and REPO_NAME_CELLBLENDER
        install_dirs = build.build_all(opts)
    else:
        # testing will use defaults
        install_dirs = {}
    
    # 3) create bundle
    # overwrite install_dirs with new values
    if opts.do_bundle:
        bundle.create_bundle(opts)
        # also extract it right away if testing is needed
        install_dirs = bundle.extract_resulting_bundle(opts)
    
    # 4) test
    if opts.do_test:
        test_all(opts, install_dirs)
        
    # 5) store the release 
    if opts.store_build:
        if opts.release_version != INTERNAL_RELEASE_NO_VERSION:
            # release
            if os.path.exists(MCELL_BUILD_INFRASTRUCTURE_RELEASES_DIR):
                log("Copying release '" + opts.result_bundle_archive_path + "'  to '" + MCELL_BUILD_INFRASTRUCTURE_RELEASES_DIR + "'.")
                shutil.copy(opts.result_bundle_archive_path, MCELL_BUILD_INFRASTRUCTURE_RELEASES_DIR)
            else:
                fatal_error("Could not find directory '" + MCELL_BUILD_INFRASTRUCTURE_RELEASES_DIR + 
                            "', release was not stored but can be found as '" + opts.result_bundle_archive_path + "'.")
        else:
            if os.path.exists(MCELL_BUILD_INFRASTRUCTURE_BUILDS_DIR):
                log("Copying release '" + opts.result_bundle_archive_path + "'  to '" + MCELL_BUILD_INFRASTRUCTURE_BUILDS_DIR + "'.")
                shutil.copy(opts.result_bundle_archive_path, MCELL_BUILD_INFRASTRUCTURE_BUILDS_DIR)
            else:
                fatal_error("Could not find directory '" + MCELL_BUILD_INFRASTRUCTURE_BUILDS_DIR + 
                            "', release was not stored but can be found as '" + opts.result_bundle_archive_path + "'.")
    
    log("--- All tasks finished successfully ---")
    

if __name__ == "__main__":
    main()
    
