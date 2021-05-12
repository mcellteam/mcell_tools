#!/bin/bash

python setup.py bdist_wheel || exit 1
twine upload dist/*
