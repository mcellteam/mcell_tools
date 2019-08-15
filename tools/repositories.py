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

# NOTE: usage of some a git library was considered, however, it was not clear whether they
# really work on Windows and MacOS, therefore a simple wrapper functions were created instead 

import os
from utils import *
from settings import *

BASE_URL = 'https://github.com/mcellteam/'
REPOSITORIES = [REPO_NAME_MCELL, REPO_NAME_CELLBLENDER] # ..., 'nfsimCInterface'  ]
MIN_GIT_VERSION= 'git version 1.9' 
ORIGIN = 'origin'

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
    

def clone(name, opts):
    log("Repository '" + name + "' does not exist, cloning it...")
    run_git_w_ec_check(['clone', BASE_URL + name], opts.top_dir)
    
    # init and update submnodules if they are present
    # will be removed once we get rid of submodules
    repo_dir = os.path.join(opts.top_dir, name)
    if (os.path.exists(os.path.join(repo_dir, '.gitmodules'))):
        run_git_w_ec_check(['submodule', 'init'], repo_dir)
        run_git_w_ec_check(['submodule', 'update'], repo_dir)


def fetch(name, opts):
    run_git_w_ec_check(['fetch'], os.path.join(opts.top_dir, name))


def checkout(name, opts):
    log("Checking out branch '" + opts.branch + "'")

    repo_dir = os.path.join(opts.top_dir, name)
    
    # first check that the branch exists on remote
    branches = run_git_w_ascii_output(['branch', '-r'], repo_dir)
    full_name = ORIGIN + '/' + opts.branch 
    if not full_name in branches: # FIXME: improve check, we are just checking a substring
        fatal_error("Error: remote branch '" + opts.branch + "' does not exit in repo '" + name + "'.")
    
    # then we need to check that the branch is clean before we switch
    status = run_git_w_ascii_output(['status'], repo_dir)
    print(status)
    if not 'nothing to commit, working directory clean' in status:
        fatal_error("Error: repository '" + name + "' is not clean. "
                    "Either clean it manually or if you are sure that there are "
                    "no changes that need to be kept run this script with '-c'.")
    
    # finally we can switch
    run_git_w_ec_check(['checkout', opts.branch], repo_dir)


def update(name, opts):
    log("Updating repository '" + name + "'.")
    run_git_w_ec_check(['pull'], os.path.join(opts.top_dir, name))
    

def get_or_update_repository(name, opts):
    # does the directory exist?
    repo_path = os.path.join(opts.top_dir, name)
    if not os.path.exists(repo_path):
        clone(name, opts)
    else:
        log("Repository '" + name + "' already exists, no need to clone it.")
    
    fetch(name, opts)
    
    # checkout the required branch
    checkout(name, opts)
    
    # update 
    if opts.update:
        update(name, opts)


def get_or_update(opts):
    check_git_version()
    
    for name in REPOSITORIES:
        log("--- Preparing repository '" + name + "' ---")
        get_or_update_repository(name, opts)
    