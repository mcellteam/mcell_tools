# mcell_tools

This repository will contain all tools to clone repositories build a whole bundle.
The idea is to be able to clone just this repo, then run a single script 
that will clone or update all the required repositories, build everything that is necessary, and assemble a blender bundle.
The resulting bundle will then be used in testing that the tools in this repo also run.

Ideally, the only thing the testing system should do it to clone this repo,
execute the run.py script and then collect results to be presented. 
 
This repo does not need any other repository to be cloned.
 