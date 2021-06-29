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

PVER=`python --version 2>&1`
echo $PVER
if [[ $PVER != Python\ 3.9* ]]; then
  # gamer and other components need to be built with python3.5 libraries
  # and they use the default python3 executable to determine the location 
  # of the libraries  
  echo "Switching to conda python 3.9"
  eval "$(conda shell.bash hook)"
  conda activate py39 || exit 1
fi

# TODO: check that mcell_tools has the right branch 
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
	BUILD_INFRA_DIR=/home/ahusar/mcell/mcell_build_infrastructure_data/
	if [ ! -d $BUILD_INFRA_DIR ]; then
		BUILD_INFRA_DIR=/cnl/mcelldata/mcell_build_infrastructure_data/
	fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
	BUILD_INFRA_DIR=/Volumes/mcell_build_infrastructure_data
elif [[ "$OSTYPE" == "msys" ]]; then
	BUILD_INFRA_DIR=Z://
else
	echo "Unsupported OS."
	exit 1
fi

if [ ! -d $BUILD_INFRA_DIR ]; then
	echo "Directory $BUILD_INFRA_DIR with build data was not found."
	exit 1
fi

# note, there must not be system python other than 3.5 installed on MacOS otherwise cmake always selects that one
# maybe it can be fixed somehow but not sure how yet

if "$EXTRA_ARG" == "pkgtest"; then
	STEPS="-34"
	EXTRA_ARG=""
else
	STEPS="-1234"	 
fi
	
./run.py $EXTRA_ARG $STEPS -u -z -b $BRANCH -i -r $VER --store-build -m $BUILD_INFRA_DIR
