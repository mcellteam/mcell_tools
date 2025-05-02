"""
Copyright (C) 2019 by
The Salk Institute for Biological Studies and
Pittsburgh Supercomputing Center, Carnegie Mellon University

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

# NOTE: usage of some a git library was considered, however, it was not clear whether they
# really work on Windows and MacOS, therefore a simple wrapper functions were created instead 

import os
import time
import datetime

from utils import *
from build_settings import *

BASE_URL = 'https://github.com/mcellteam/'

BASE_URL_HTTPS = 'https://github.com/mcellteam/'
BASE_URL_SSH = 'git@github.com:mcellteam/'
PRIVATE_BASE_URL_SSH = 'git@github.com:mcellteam/'
GIT_SUFFIX = '.git'
BASE_REPOSITORIES = [
    REPO_NAME_MCELL, REPO_NAME_LIBBNG, REPO_NAME_CELLBLENDER, 
    REPO_NAME_MCELL_TESTS, REPO_NAME_MCELL_TOOLS, 
    REPO_NAME_NEUROPIL_TOOLS, REPO_NAME_MESH_TOOLS,
    # REPO_NAME_GAMER1, - TODO
    REPO_NAME_VTK
]

FORKED_REPOSITORIES = [REPO_NAME_NFSIM, REPO_NAME_NFSIMCINTERFACE, REPO_NAME_BIONETGEN, REPO_NAME_GAMER]


ALL_REPOSITORIES = BASE_REPOSITORIES + FORKED_REPOSITORIES
 

REPOSITORIES_ALLOWED_TO_BE_DIRTY = [REPO_NAME_MCELL_TESTS, REPO_NAME_MCELL_TOOLS, REPO_NAME_GAMER, REPO_NAME_BIONETGEN]


# FORKED_REPOSITORY_BRANCH_PREFIX = 'mcell_'
FORKED_REPOSITORY_BRANCH_PREFIX = ''

MIN_GIT_VERSION= 'git version 1.9' 
ORIGIN = 'origin'

GAMER_BASE_URL = 'https://github.com/ctlee/'
GAMER_BRANCH = 'master'


def run_git_w_ascii_output(args, cwd):
    cmd = ['git']
    cmd += args 
    return run_with_ascii_output(cmd, cwd)


def run_git_w_ec_check(args, cwd):
    cmd = ['git']
    cmd += args
    #print(str(cmd)) 
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
    run_git_w_ec_check(['clone', base_url + name + GIT_SUFFIX], opts.top_dir)


def fetch(name, opts):
    run_git_w_ec_check(['fetch'], os.path.join(opts.top_dir, name))


def get_default_branch(name, branch):
    if branch.startswith(BRANCH_PREFIX_MCELL4):
        return DEFAULT_BRANCH_MCELL4
    elif name in FORKED_REPOSITORIES:
        return FORKED_REPOSITORY_BRANCH_PREFIX + DEFAULT_BRANCH 
    else:
        return DEFAULT_BRANCH


def checkout(name, opts, branch):
    log("Checking out branch '" + branch + "'")

    repo_dir = os.path.join(opts.top_dir, name)
    
    # first check that the branch exists on remote
    branches = run_git_w_ascii_output(['branch', '-r'], repo_dir)
    full_name = ORIGIN + '/' + branch 
    if not full_name in branches: # FIXME: improve check, we are just checking a substring
        orig_branch = branch
        branch = get_default_branch(name, branch)
        warning("Remote branch '" + orig_branch + "' does not exit in repo '" + name + "', defaulting to '" + branch + "'.")

    full_name2 = ORIGIN + '/' + branch 
    if not full_name2 in branches: # FIXME: improve check, we are just checking a substring
        orig_branch = branch
        branch = DEFAULT_BRANCH
        warning("Remote default branch '" + orig_branch + "' does not exit in repo '" + name + "', defaulting to '" + branch + "'.")
    
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


def pull_repository(name, opts, base_url, branch):
    run_git_w_ec_check(['pull'], os.path.join(opts.top_dir, name))


def push_repository(name, opts, base_url, branch):
    run_git_w_ec_check(['push'], os.path.join(opts.top_dir, name))


def reset_hard_repository(name, opts, base_url, branch):
    run_git_w_ec_check(['reset', '--hard'], os.path.join(opts.top_dir, name))


def tag_repository(name, opts, base_url, branch):
    run_git_w_ec_check(['tag', branch, '-m', branch], os.path.join(opts.top_dir, name))


def merge_repository(name, opts, base_url, branch):
    # not all branches must be present
    out = run_git_w_ascii_output(['merge', branch], os.path.join(opts.top_dir, name))
    print(out)


def run_on_all_repositories(opts, function):
    if opts.ssh:
        base_url_w_prefix = BASE_URL_SSH
    else:
        base_url_w_prefix = BASE_URL_HTTPS
    
    for name in BASE_REPOSITORIES:
        log("--- Preparing repository '" + name + "' ---")
        function(name, opts, base_url_w_prefix, opts.branch)    

    for name in FORKED_REPOSITORIES:
        log("--- Preparing repository '" + name + "' ---")
        
        if not opts.branch.startswith(BRANCH_PREFIX_MCELL4):
            # use mcell_ prefix
            branch_name = FORKED_REPOSITORY_BRANCH_PREFIX + opts.branch
        else:
            branch_name = opts.branch
            
        function(name, opts, base_url_w_prefix, branch_name)
    
    if opts.use_private_repos:
        log("--- Preparing repository '" + REPO_NAME_MCELL_TEST_PRIVATE + "' ---")
        function(REPO_NAME_MCELL_TEST_PRIVATE, opts, PRIVATE_BASE_URL_SSH, opts.branch) 
    


def get_or_update(opts):
    check_git_version()
    run_on_all_repositories(opts, get_or_update_repository)
    

def pull(opts):
    check_git_version()
    run_on_all_repositories(opts, pull_repository)


def push(opts):
    check_git_version()
    run_on_all_repositories(opts, push_repository)

    
def reset_hard(opts):
    check_git_version()
    run_on_all_repositories(opts, reset_hard_repository)


def tag(opts):
    check_git_version()
    run_on_all_repositories(opts, tag_repository)

def merge(opts):
    check_git_version()
    run_on_all_repositories(opts, merge_repository)
    
def create_version_file(opts):
    if not os.path.exists(opts.work_dir):
        os.makedirs(opts.work_dir)
    
    version_file = os.path.join(opts.work_dir, RELEASE_INFO_FILE)
    with open(version_file, "w", encoding="utf-8") as f:
        f.write("CellBlender release: " + opts.release_version + "\n")
        now = datetime.datetime.now()
        f.write("Built on " + now.strftime("%Y-%m-%d %H:%M") + " " + str(time.tzname) + "\n")
        f.write("OS: " + platform.platform() + "\n")
        
        cmd = ['gcc', '--version']
        res = run_with_ascii_output(cmd, cwd='.')
        if cmd:
            f.write("GCC: " + res.split('\n')[0] + "\n")
        
        f.write("\n")
        
        for repo_name in ALL_REPOSITORIES:
            branch = run_git_w_ascii_output(['describe', '--all'], cwd=os.path.join(opts.top_dir, repo_name))
            commit = run_git_w_ascii_output(['log', '-1', '--pretty="%H"'], cwd=os.path.join(opts.top_dir, repo_name))
            f.write(repo_name + ": " + commit + " (" + branch + ")\n")
    
