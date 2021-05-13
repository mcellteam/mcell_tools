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
if [ "$PVER_SHORT" != "Python 3.8" ]; then
  echo "Switching to conda python 3.8"
  eval "$(conda shell.bash hook)"
  conda activate py38 || exit 1
fi

if [ ! -d $BUILD_INFRA_DIR ]; then
	echo "Directory $BUILD_INFRA_DIR with build data was not found."
	exit 1
fi

./run.py $EXTRA_ARG -12 -y -u -z -b $BRANCH -i -r $VER -m $BUILD_INFRA_DIR 


