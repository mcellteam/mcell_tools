#!/bin/bash

BLENDER_DIR=$1
GAMER_BUILD_DIR=$2

echo "Executing $0 in `pwd`"
echo "BLENDER_DIR: $BLENDER_DIR"
echo "GAMER_BUILD_DIR: $GAMER_BUILD_DIR"


VER=`python3 --version`
VER_SHORT=${VER%.*}
if [ "$VER_SHORT" != "Python 3.5" ]; then
  # gamer needs Python 3.5 to be the main executable
  # we need to switch environment, so this is the reason why we do this build in a bash script 
  eval "$(conda shell.bash hook)"
  conda activate py35 || exit 1
fi

echo "The current python3 is:"
echo `which python3`
python3 --version

# and blender to be found in PATH
export PATH=$BLENDER_DIR:$PATH

# override -DPYBIND11_PYTHON_VERSION=3.5 is needed for MacOS because even with 
# the default python being the one from conda, pybind11 uses the system libs   
# TODO: add -DCMAKE_CXX_FLAGS=-D\'__has_cpp_attribute(x)=0\'
cmake ../../../gamer -DBUILD_BLENDGAMER=ON -DCMAKE_BUILD_TYPE=Release -DBLENDER_VERSION=2.79 -DPYBIND11_PYTHON_VERSION=3.5 || exit 1

 