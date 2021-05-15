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
  pip3 install lxml numpy matplotlib
```

And this is how the test are run:

```
  cd ../mcell_tests
  python3 run-tests.py # optional argument -c TEST_CONFIG selects test configuration, test_configs/default.tomp is the default config
```
