#!/bin/bash

VER=$1
BRANCH=$2
EXTRA_ARG=$3

if [ "$VER" == "" ]; then
   echo "Error: version ID must be entered"
fi

if [ "$BRANCH" == "" ]; then 
   BRANCH="development"
fi

# TODO: check that mcell_tools has the right branch 
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
	BUILD_INFRA_DIR=/home/ahusar/mcell/mcell_build_infrastructure_data/
	if [ ! -d $BUILD_INFRA_DIR ]]; then
		BUILD_INFRA_DIR=/mnt/hgfs/mcell_build_infrastructure_data/
	fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
	echo "TODO"
elif [[ "$OSTYPE" == "msys" ]]; then
	BUILD_INFRA_DIR=z:\\
else
	echo "Unsupported OS."
	exit 1
fi

if [ ! -d $BUILD_INFRA_DIR ]]; then
	echo "Directory $BUILD_INFRA_DIR with build data was not found."
	exit 1
fi


./run.py $EXTRA_ARG -1234 -u -z -b $BRANCH -i -r $VER --store-build -m $BUILD_INFRA_DIR
