#!/bin/bash

BLENDER_DIR=$1
GAMER_BUILD_DIR=$2

echo "Executing $0 in `pwd`"
echo "BLENDER_DIR: $BLENDER_DIR"
echo "GAMER_BUILD_DIR: $GAMER_BUILD_DIR"


VER=`python3 --version`
if [[ $VER == *"Python 3.5"* ]]; then
  echo "It's there!"
fi

echo "The current python3 is:"
echo `which python3`
python3 --version

# and blender to be found in PATH
export PATH=$BLENDER_DIR:$PATH

# debian8 has only gcc-4.9 by default, pybind cannot be compiled with it 
# (although gcc-4.9 supports C++14 and it should work in theory, maybe jusr gamer uses some woeird pybind11 version) 

COMPILER_OVERRIDE=""
UN=`uname -a`
if [[ $UN == *"deb8u1"* ]]; then
  COMPILER_OVERRIDE="-DCMAKE_C_COMPILER=/home/tester/tools/gcc-7.5.0/bin/gcc -DCMAKE_CXX_COMPILER=/home/tester/tools/gcc-7.5.0/bin/g++ "
fi

# override -DPYBIND11_PYTHON_VERSION=3.5 is needed for MacOS because even with 
# the default python being the one from conda, pybind11 uses the system libs   
cmake ../../../gamer -DBUILD_BLENDGAMER=ON -DCMAKE_BUILD_TYPE=Release -DBLENDER_VERSION=2.93 -DPYBIND11_PYTHON_VERSION=3.5 $COMPILER_OVERRIDE || exit 1

 