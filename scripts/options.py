"""
Copyright (C) 2019 by
The Salk Institute for Biological Studies and
Pittsburgh Supercomputing Center, Carnegie Mellon University

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

import os
import platform
import socket
import datetime
import argparse

from build_settings import *


class Options:
    def __init__(self):
        self.update = False
        self.clean = False
        self.ignore_dirty = False
        self.debug = False
        self.ssh = False
        self.use_private_repos = False
        self.mcell_python = None

        self.do_not_build_gamer = False
        self.do_not_sign_package = False

        self.only_cellblender_mcell = False
        self.only_pypi_wheel = False

        self.do_repos = False
        self.do_build = False
        self.do_bundle = False
        self.do_test = False

        self.branch = DEFAULT_BRANCH

        self.release_version = INTERNAL_RELEASE_NO_VERSION
        self.store_build = False

        # set by set_result_bundle_archive_name,
        # needs release_version
        self.result_bundle_archive_path = None

        # for developers it might be useful to clone the repositories as ssh
        self.ssh_for_clone = False
        fqdn = socket.getfqdn()
        for dns in DEFAULT_DNS_FOR_SSH_CLONE:
            if dns in fqdn:
                self.ssh_for_clone = True

        # diverse help and info methods
        self.print_platform_info = False

        # using os.getcwd() + '..' does not work with links as expected
        self.top_dir = os.path.dirname(get_cwd_no_link())
        self.work_dir = os.path.join(self.top_dir, REPO_NAME_MCELL_TOOLS, WORK_DIR_NAME)

        # might be overridden in case when the buid system builds its own cmake
        self.cmake_executable = CMAKE_SYSTEM_EXECUTABLE

        self.mcell_build_infrastructure_dir = DEFAULT_MCELL_BUILD_INFRASTRUCTURE_DATA_DIR
        self.prebuilt_blender_w_python_base = ''
        self.mcell_build_infrastructure_releases_dir = ''
        self.mcell_build_infrastructure_builds_dir = ''
        self.set_mcell_infrastructure_dirs()


    def set_mcell_infrastructure_dirs(self):
        assert self.mcell_build_infrastructure_dir

        if platform.system() == 'Linux':
            simpler_system =  'Linux'
        elif platform.system() == 'Darwin':
            simpler_system = 'macOS'
        elif 'Windows' in platform.system():
            simpler_system = 'Windows'
        else:
            assert False

        common_name = BUILD_DIR_BLENDER + '-' + BLENDER_FULL_VERSION + '-' + simpler_system + '-' + platform.machine()
        self.prebuilt_blender_w_python_base = \
            os.path.join(self.mcell_build_infrastructure_dir, 'prebuilt_blender_w_python', 'base', common_name)

        # versions_info = BUILD_SUBDIR_BLENDER_OS_BASED
        self.prebuilt_blender_w_python_override = \
            os.path.join(self.mcell_build_infrastructure_dir, 'prebuilt_blender_w_python', 'overrides', common_name)


        self.mcell_build_infrastructure_releases_dir = \
            os.path.join(self.mcell_build_infrastructure_dir, 'releases')
        self.mcell_build_infrastructure_builds_dir = \
            os.path.join(self.mcell_build_infrastructure_dir, 'builds')


    def __repr__(self):
        attrs = vars(self)
        return ", ".join("%s: %s" % item for item in attrs.items())

    def set_result_bundle_archive_path(self):
        now = datetime.datetime.now()

        if platform.system() == 'Linux':
            import distro
            os_name = distro.id().capitalize() + '-' + distro.version() + '-' + platform.machine()
        elif platform.system() == 'Darwin':
            os_name = '-'.join(platform.platform().split('-')[:3])
        else:   # Windows
            os_name = platform.system() + '-' + platform.release() + '-' + platform.machine()

        if self.only_cellblender_mcell:
            archive_name = \
                CELLBLENDER_MCELL_PLUGIN + '-' + self.release_version + '-' + \
                os_name + '-' + now.strftime("%Y%m%d") + '.' + BUNDLE_EXT
            self.result_bundle_archive_path = os.path.join(self.work_dir, archive_name)
        else:
            archive_name = \
                BUILD_SUBDIR_BLENDER + '-' + self.release_version + '-' + 'Python-' + platform.python_version() + '-' + \
                os_name + '-' + now.strftime("%Y%m%d") + '.' + BUNDLE_EXT

            self.result_bundle_archive_path = os.path.join(self.work_dir, BUILD_DIR_BLENDER, archive_name)

    @staticmethod
    def create_argparse():
        parser = argparse.ArgumentParser(description='MCell & CellBlender build tool')
        # NOTE: maybe add verbosity level? - for now, all information is printed out
        parser.add_argument('-u', '--update', action='store_true', help='update repositories is they are already checked out')
        parser.add_argument('-c', '--clean', action='store_true', help='clean data from previous build')
        parser.add_argument('-i', '--ignore-dirty', action='store_true', help='ignore dirty repositories (not supported yet)')
        parser.add_argument('-d', '--debug', action='store_true', help='build debug variant of mcell')
        parser.add_argument('-s', '--ssh', action='store_true', help='use ssh to clone repositories')
        parser.add_argument('-z', '--use-private-repos', action='store_true', help='use mcell private repositories')
        parser.add_argument('-g', '--do-not-build-gamer', action='store_true', help='do not build gamer')
        parser.add_argument('-n', '--do-not-sign-package', action='store_true', help='do not sign package on MacOS')

        parser.add_argument('-y', '--mcell-python', type=str, help='Python version to be used in MCell build, allowed values: 3.11 or higher')

        parser.add_argument('-m', '--mcell-infrastructure-dir', type=str, help='path to mcell_build_infrastructure_data directory')
        parser.add_argument('-r', '--release', type=str, help='make a release, set release version')
        parser.add_argument('-t', '--store-build', action='store_true', help='store build in mcelldata directory')
        parser.add_argument('-o', '--only-cellblender-mcell', action='store_true', help='build only mcell and cellblender as a blender plugin, do not include blender or other plugins')
        parser.add_argument('-w', '--only-pypi-wheel', action='store_true', help='build only mcell.so/dyl and build a wheel as a PyPi package')

        parser.add_argument('-b', '--branch', type=str, help='branch to checkout, tries to change the current branch if the branch is different from what is selected and there are no changes')

        parser.add_argument('-1', '--do-repos', action='store_true', help='get repositories (done by default when none of the "1234" args are set)')
        parser.add_argument('-2', '--do-build', action='store_true', help='run build (done by default when none of the "1234" args are set)')
        parser.add_argument('-3', '--do-bundle', action='store_true', help='build bundle (done by default when none of the "1234" args are set)')
        parser.add_argument('-4', '--do-test', action='store_true', help='run tests (done by default when none of the "1234" args are set)')

        parser.add_argument('-p', '--print-platform-info', action='store_true', help='print platform-dependent names of packages')


        return parser


    def process_opts(self):

        parser = Options.create_argparse()
        args = parser.parse_args()
        print(args)

        if args.update:
            self.update = True
        if args.ssh:
            self.ssh = True
        if args.clean:
            self.clean = True
        if args.ignore_dirty:
            self.ignore_dirty = True
        if args.debug:
            self.debug = True

        if args.only_cellblender_mcell:
            self.only_cellblender_mcell = True

        if args.only_pypi_wheel:
            self.only_pypi_wheel = True

        if args.do_not_build_gamer:
            self.do_not_build_gamer = True

        if args.do_not_sign_package:
            self.do_not_sign_package = True

        if args.use_private_repos:
            self.use_private_repos = True

        if args.mcell_python:
            ver = args.mcell_python
            if ver >= '3.11':
                sys.exit("The only supported Python versions are 3.11 and higher")
            self.mcell_python = args.mcell_python

        if args.branch:
            self.branch = args.branch

        if args.mcell_infrastructure_dir:
            self.mcell_build_infrastructure_dir = args.mcell_infrastructure_dir
            self.set_mcell_infrastructure_dirs()

        if args.release:
            self.release_version = args.release
        if args.store_build:
            self.store_build = True

        self.do_repos = args.do_repos
        self.do_build = args.do_build
        self.do_bundle = args.do_bundle
        self.do_test = args.do_test

        self.set_result_bundle_archive_path()

        if args.print_platform_info:
            self.print_platform_info = True
            return

        # final processing

        # no specific task was set, do all
        if not (self.do_repos or self.do_build or self.do_bundle or self.do_test or self.only_cellblender_mcell):
            self.do_repos = True
            self.do_build = True
            #self.do_bundle = True
            #self.do_test = True
