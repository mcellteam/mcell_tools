#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

find ./ -name "*.py" -type f -exec python $SCRIPT_DIR/replace_license.py $SCRIPT_DIR/gpl_py.txt $SCRIPT_DIR/mit_py.txt {} \;

# not sure how to make a loop with *.
find ./ -name "*.c" -type f -exec python $SCRIPT_DIR/replace_license.py $SCRIPT_DIR/gpl_c.txt $SCRIPT_DIR/mit_c.txt {} \;
find ./ -name "*.cpp" -type f -exec python $SCRIPT_DIR/replace_license.py $SCRIPT_DIR/gpl_c.txt $SCRIPT_DIR/mit_c.txt {} \;
find ./ -name "*.h" -type f -exec python $SCRIPT_DIR/replace_license.py $SCRIPT_DIR/gpl_c.txt $SCRIPT_DIR/mit_c.txt {} \;
find ./ -name "*.inl" -type f -exec python $SCRIPT_DIR/replace_license.py $SCRIPT_DIR/gpl_c.txt $SCRIPT_DIR/mit_c.txt {} \;
find ./ -name "*.i" -type f -exec python $SCRIPT_DIR/replace_license.py $SCRIPT_DIR/gpl_c.txt $SCRIPT_DIR/mit_c.txt {} \;
