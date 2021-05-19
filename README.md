# mcell_tools

This repository contains all tools to clone MCell repositories and build them.

Required system packages (on Debian 9) are:

```
  sudo apt install git cmake build-essential bison flex swig python3 python3-dev libboost-dev zip
```

To checkout all the repositories and build mcell along with other tools, run the following commands:

```
  mkdir mcell
  git clone https://github.com/mcellteam/mcell_tools.git
  cd mcell_tools
  python3 run.py # optional argument -b BRANCH_NAME selects branch, mcell4_dev is the default branch
```
  
The resulting build directory of mcell is then located in work/build_mcell.


To run tests afterwards, these packages need to be installed (on Debian 9):

```
  sudo apt install python3-pip python3-tk
  pip3 install toml pyparsing lxml pyyaml psutil matplotlib pathlib pandas
```

And this is how the test are run:

```
  cd ../mcell_tests
  python3 run-tests.py # optional argument -c TEST_CONFIG selects test configuration, test_configs/default.tomp is the default config
```


## Windows System Setup

These sections desribe how to setup a Windows build&test system. 

### 1) Downloads

https://visualstudio.microsoft.com/vs/features/cplusplus/
- install C++ compiler, might need recent windows upgrades

https://repo.msys2.org/distrib/x86_64/msys2-x86_64-20210105.exe

https://github.com/cmderdev/cmder/releases/download/v1.3.17/cmder.zip

https://www.eclipse.org/downloads/packages/

https://www.python.org/ftp/python/3.5.0/python-3.5.0-amd64.exe

https://github.com/Kitware/CMake/releases/download/v3.15.5/cmake-3.15.5-win64-x64.msi

https://sourceforge.net/projects/mingw-w64/files/Toolchains%20targetting%20Win32/Personal%20Builds/mingw-builds/installer/mingw-w64-install.exe/download

### 2) Add Python, visual studio, mingw, msys, and cmake to PATH

Example PATH value for tools under c:\mcell\tools and user name tester:

C:\mcell\tools\mingw-w64\x86_64-8.1.0-posix-seh-rt_v6-rev0\mingw64\bin;C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.28.29333\bin\Hostx64\x64;C:\mcell\tools\Python35;C:\mcell\tools\msys64\usr\bin;C:\Users\tester\AppData\Local\Microsoft\WindowsApps;C:\mcell\tools\cmder\vendor\git-for-windows\mingw64\bin;C:\mcell\tools\cmder\vendor\git-for-windows\usr\bin;C:\mcell\tools\cmder


### 3) Make a python3.exe copy

cp /c/mcell/tools/Python35/python.exe /c/mcell/tools/Python35/python3.exe

### 4) Install python libs
Old versions of pip cannot install the dependencies and newer version e.g. 20.x is not compatible with 3.5
so we must use 10.0.

python.exe -m pip install pip==10.0.1
python -m pip install toml pyparsing lxml pyyaml psutil

### 5) Install zip and gcc

pacman -S zip unzip flex bison make swig

### 6) Fix python installation according to notes in cellblender/windows_build_readme.txt

### 7) Remove unzip from git installation
which unzip
-> make sure that unzip comes from msys

### 8) Update python.py according to notes in cellblender
