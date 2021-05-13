#!/bin/bash -x

rm -r dist
python setup.py bdist_wheel -p manylinux1_x86_64 || exit 1
twine upload --repository testpypi dist/*
