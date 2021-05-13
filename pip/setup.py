import setuptools
import platform
import sys
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = 'mcell/utils/pybind11_test/build/'

if platform.system() == 'Linux':
    lib_name = 'mcell.cpython-35m-x86_64-linux-gnu.so'
    dst_dir = 'lib/python3.5/lib-dynload' # requires version-specific path...
elif platform.system() == 'Darwin':
    assert False, "TODO"
    lib_name = 'mcell.cpython-35m-x86_64-darwin.so' # ???
    dst_dir = 'lib-dynload/python3.5' # requires specific path...
elif 'Windows' in platform.system():
    assert False, "TODO"
    lib_name = 'mcell.cpython-35m-x86_64-darwin.so' # ???
    dst_dir = 'DLLs' # seem ok
else:
    sys.exit("Operating system '" + platform.system() + "' is not supported in this build system yet.")
    
lib_path = os.path.join(THIS_DIR, '..', '..', BUILD_DIR, lib_name)     
    
setuptools.setup(
     name='mcell',  
     version='4.98.4', # todo: set automatically - has to be number
      
     data_files=[(dst_dir, [lib_path])], 
     author="Salk Institute for Biologocal Studies",
     author_email="ahusar@salk.edu",
     description="MCell4",
     long_description="MCell4",
     long_description_content_type="text/markdown",
     url="https://www.mcell.org",
     download_url="https://mcell.org/download.html",
     python_requires='==3.5.*', # which version to support? is 3.8 and 3.9 compatible?
     classifiers=[
         "Development Status :: 4 - Beta",
         "License :: OSI Approved :: GNU General Public License v2 (GPLv2)"
     ],
     zip_safe=True
)
