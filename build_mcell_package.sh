#!/bin/bash

VER=$1
BRANCH=$2
EXTRA_ARG=$3

if [ "$VER" == "" ]; then
   echo "Error: version ID must be entered"
   exit 1
fi

if [ "$BRANCH" == "" ]; then 
   BRANCH="mcell4_dev"
fi

PVER=`python --version`
PVER_SHORT=${PVER%.*}
if [ "$PVER_SHORT" != "Python 3.5" ]; then
  # gamer and other components need to be built with python3.5 libraries
  # and they use the default python3 executable to determine the location 
  # of the libraries  
  echo "Switching to conda python 3.5"
  eval "$(conda shell.bash hook)"
  conda activate py35 || exit 1
fi

./run.py $EXTRA_ARG -12 -o -4 -u -z -b $BRANCH -i -r $VER --store-build
