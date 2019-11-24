# mcell_tools

This repository contains all tools to clone repositories build a whole bundle and test it.

Required system packages are:

```
  apt install git cmake build-essential bison flex swig python3 python3-dev libboost-dev zip
```

To checkout all the repositories and build mcell along with other tools, run the following commands:

```
  mkdir mcell
  git clone https://github.com/mcellteam/mcell_tools.git
  cd mcell_tools
  python3 run.py # optional argument -b BRANCH_NAME selects branch, testing_infrastructre is the default branch
```
  
The resulting build directory of mcell is then located in work/build_mcell. 