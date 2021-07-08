"""
Copyright (C) 2019 by
The Salk Institute for Biological Studies and
Pittsburgh Supercomputing Center, Carnegie Mellon University

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

"""
This module contains diverse utility functions shared among all mcell-related 
Python scripts.
"""

import os
import sys
import subprocess
import shutil
import platform
import multiprocessing
from threading import Timer
from subprocess import Popen, PIPE
          

def get_cwd_no_link():
    # get current working directory even though we are in a symlinked directory
    # the shell argument must be set to True in this case
    if 'Windows' in platform.system():
        res = os.getcwd()
    else:
        cwd = Popen(['pwd'], stdout=PIPE, shell=True).communicate()[0].strip()
        res = cwd.decode('ascii')
     
    return res
          

def kill_proc(proc, f, timeout_is_fatal):
    proc.kill()
    f.write("Terminated after timeout")
    if timeout_is_fatal:
        sys.exit(1)

    
def print_file(file_name):
    with open(file_name, "r") as fin:
        for line in fin:
            print(line)


def run_with_ascii_output(cmd, cwd):
    # does not return exit code, neither provides timeout
    return Popen(cmd, cwd=cwd, stdout=PIPE).communicate()[0].strip().decode('ascii')

    
def run_with_ascii_output_err(cmd, cwd):
    # does not return exit code, neither provides timeout
    return Popen(cmd, cwd=cwd, stderr=PIPE).communicate()[1].strip().decode('ascii')


def execute(cmd, cwd, timeout_sec, timeout_is_fatal, outfile, shell=False, env=None):
    if shell:
        # for shell=True, the command must be a single string
        cmd = str.join(" ", cmd)
    
    proc = Popen(cmd, shell=shell, cwd=cwd, stdout=outfile, stderr=subprocess.STDOUT, env=env)
    timer = Timer(timeout_sec, kill_proc, [proc, outfile, timeout_is_fatal])
    try:
        timer.start()
        exit_code = proc.wait()
    finally:
        timer.cancel()
        
    return exit_code


# can be simplified by using subprocess.run from Python 3.5
def run(
        cmd, 
        cwd=os.getcwd(),
        fout_name="", 
        append_path_to_output=False, 
        print_redirected_output=False, 
        timeout_sec=600,
        timeout_is_fatal = True, 
        verbose=True,
        shell=False,
        extra_env=None  # this can be
        ):
    if verbose:
        log("    Executing: '" + str.join(" ", cmd) + "' " + str(cmd) + " in '" + cwd + "'")

    extended_env = os.environ.copy()
    if extra_env is not None:
        # append extra env vars
        for k,v in extra_env.items():
            extended_env[k] = v    

    if fout_name:
        if append_path_to_output:
            full_fout_path = os.path.join(cwd, fout_name)
        else:
            full_fout_path = fout_name
    
        with open(full_fout_path, "w") as f:
            f.write("cwd: " + cwd + "\n")
            f.write(str.join(" ", cmd) + "\n")  # first item is the command being executed
            
            # run the actual command
            exit_code = execute(cmd, cwd, timeout_sec, timeout_is_fatal, f, shell=shell, env=extended_env)

        if (print_redirected_output):
            print_file(full_fout_path)
            
    else:
        exit_code = execute(cmd, cwd, timeout_sec, timeout_is_fatal, sys.stdout, shell=shell, env=extended_env)

    if verbose:
        log("Exit code: " + str(exit_code))
    return exit_code


def log(msg):
    print("* " + msg)
    sys.stdout.flush()


def warning(msg):
    print("* Warning: " + msg)
    sys.stdout.flush()


def fatal_error(msg):
    print("* Error: " + msg)
    sys.stdout.flush()
    sys.exit(1)    
   

def check_ec(ec, cmd):
    if ec != 0:
        cmd_str = str.join(" ", cmd)
        fatal_error("Error: command '" + cmd_str + "' failed, terminating.")
        
        
def get_nr_cores():
    cpu_count = multiprocessing.cpu_count()
    if cpu_count > 1:
        return int(cpu_count/2)
    else:
        return 1
    
def recursive_overwrite(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f), 
                                    os.path.join(dest, f), 
                                    ignore)
    else:
        shutil.copy(src, dest)
