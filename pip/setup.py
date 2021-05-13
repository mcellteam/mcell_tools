import setuptools
import platform
import sys
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = 'mcell/utils/pybind11_test/build/'

if platform.system() == 'Linux':
    # TODO: copy mcell library to the current directory
    pass
elif platform.system() == 'Darwin':
    #
    pass
elif 'Windows' in platform.system():
    pass
else:
    sys.exit("Operating system '" + platform.system() + "' is not supported in this build system yet.")
    

    
setuptools.setup(
     name='mcell',  
     version='3.99.0', # todo: set automatically - has to be number
      
     py_modules=['mcell'], 
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
