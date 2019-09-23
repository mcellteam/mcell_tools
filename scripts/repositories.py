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

# NOTE: usage of some a git library was considered, however, it was not clear whether they
# really work on Windows and MacOS, therefore a simple wrapper functions were created instead 

import os
from utils import *
from build_settings import *

BASE_URL = 'https://github.com/mcellteam/'
REPOSITORIES = [REPO_NAME_MCELL, REPO_NAME_CELLBLENDER, REPO_NAME_MCELL_TESTS] # ..., 'nfsimCInterface'  ]

MIN_GIT_VERSION= 'git version 1.9' 
ORIGIN = 'origin'

GAMER_BASE_URL = 'https://github.com/ctlee/'
GAMER_BRANCH = 'master'

REPOSITORIES_ALLOWED_TO_BE_DIRTY = [REPO_NAME_MCELL_TESTS, REPO_NAME_GAMER]

def run_git_w_ascii_output(args, cwd):
    cmd = ['git']
    cmd += args 
    return run_with_ascii_output(cmd, cwd)


def run_git_w_ec_check(args, cwd):
    cmd = ['git']
    cmd += args 
    ec = run(cmd, cwd)
    check_ec(ec, cmd) 


def check_git_version():
    out = run_git_w_ascii_output(['--version'], os.getcwd())
    # TODO: just a string compre for now..
    if out >= MIN_GIT_VERSION:
        log("Checked " + out + " - ok")
    else:
        fatal_error("Required at least " + MIN_GIT_VERSION)
    

def clone(name, opts, base_url):
    log("Repository '" + name + "' does not exist, cloning it...")
    run_git_w_ec_check(['clone', base_url + name], opts.top_dir)


def fetch(name, opts):
    run_git_w_ec_check(['fetch'], os.path.join(opts.top_dir, name))


def checkout(name, opts, branch):
    log("Checking out branch '" + branch + "'")

    repo_dir = os.path.join(opts.top_dir, name)
    
    # first check that the branch exists on remote
    branches = run_git_w_ascii_output(['branch', '-r'], repo_dir)
    full_name = ORIGIN + '/' + branch 
    if not full_name in branches: # FIXME: improve check, we are just checking a substring
        fatal_error("Remote branch '" + branch + "' does not exit in repo '" + name + "'.")
    
    # then we need to check that the branch is clean before we switch
    status = run_git_w_ascii_output(['status'], repo_dir)
    print(status)
    if 'working directory clean' not in status and 'working tree clean' not in status:
        if not opts.ignore_dirty and name not in REPOSITORIES_ALLOWED_TO_BE_DIRTY:
            fatal_error("Repository '" + name + "' is not clean. "
                        "Either clean it manually or if you are sure that there are "
                        "no changes that need to be kept run this script with '-c'.")
        else:
            warning("Repository '" + name + "' is not clean, but this repo is allowed to be dirty.")
    
    # finally we can switch
    run_git_w_ec_check(['checkout', branch], repo_dir)

    # init and update submnodules if they are present
    # will be removed once we get rid of submodules
    if (os.path.exists(os.path.join(repo_dir, '.gitmodules'))):
        run_git_w_ec_check(['submodule', 'init'], repo_dir)
        run_git_w_ec_check(['submodule', 'update'], repo_dir)


def update(name, opts):
    log("Updating repository '" + name + "'.")
    run_git_w_ec_check(['pull'], os.path.join(opts.top_dir, name))
    

def get_or_update_repository(name, opts, base_url, branch):
    # does the directory exist?
    repo_path = os.path.join(opts.top_dir, name)
    if not os.path.exists(repo_path):
        clone(name, opts, base_url)
    else:
        log("Repository '" + name + "' already exists, no need to clone it.")
    
    fetch(name, opts)
    
    # checkout the required branch
    checkout(name, opts, branch)
    
    # update 
    if opts.update:
        update(name, opts)


def get_or_update(opts):
    check_git_version()
    
    for name in REPOSITORIES:
        log("--- Preparing repository '" + name + "' ---")
        get_or_update_repository(name, opts, BASE_URL, opts.branch)
    
    # for gamer, we alwaya use the master branch
    # TODO: we might need to be making release branches, but let's stay with this solution for now
    get_or_update_repository(REPO_NAME_GAMER, opts, GAMER_BASE_URL, GAMER_BRANCH) 
    
    
    