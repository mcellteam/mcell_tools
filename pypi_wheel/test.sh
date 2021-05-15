#!/bin/bash -x

python -m pip uninstall mcell
python -m pip install --no-cache-dir --index-url https://test.pypi.org/simple/ mcell

python -c "import mcell"