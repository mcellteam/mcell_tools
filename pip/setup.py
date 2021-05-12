import setuptools

# TODO: register and upload

setuptools.setup(
     name='mcell',  
     version='4.99.17', # todo: set automatically - has to be number
     # todo: set automatically - what are the 
     data_files=[('lib', ['mcell.cpython-35m-x86_64-linux-gnu.so'])], 
     author="Salk Institute",
     author_email="ahusar@salk.edu",
     description="MCell4",
     long_description="MCell4",
     long_description_content_type="text/markdown",
     url="https://www.mcell.org",
     
     download_url="https://mcell.org/download.html",
     
     python_requires='==3.5.*', # which version to support? is 3.8 and 3.9 compatible?
     
     # todo: limit OSes
     platforms=['Linux'],
      
     classifiers=[
         "Development Status :: 4 - Beta",
         "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
         "Operating System :: POSIX :: Linux",  # todo: set automatically
     ],
     zip_safe=True
     )
