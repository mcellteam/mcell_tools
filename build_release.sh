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

BUILD_INFRA_DIR=/home/ahusar/mcell/mcell_build_infrastructure_data/

./run.py $EXTRA_ARG -1234 -u -z -b $BRANCH -i -r $VER --store-build -m $BUILD_INFRA_DIR
