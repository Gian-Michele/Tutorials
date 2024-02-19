# Python 
This contain some useful information on Python and how set venv for different project

### CONDA 

Some client application can be launched on python3.7 other could need higher version of python, because of that can be useful dowload a system to handle virtula environment like anaconda. The last installer can be found in: [anaconda last version](https://www.anaconda.com/products/distribution)
The installation of Anaconda can be found in [installation_link](https://docs.conda.io/projects/conda/en/stable/user-guide/install/linux.html#)

When Anaconda is installed a new venv can be created using command:

        conda create -n yourenvname python=3.7 anaconda

the activation of the env can be done  using command:

        conda activate yourenvname

when the venv is activated you can install the following package:

         pip install requests==2.20.1 asyncio==3.4.3 asyncio-nats-client==0.11.5

in order to exit from the venv use the command:

        conda deactivate

the list of venv can be liste using

        conda info -e

Install a list of packages into an environment, myenv:: (suggest search in google conda package)

    conda install -n myenv scipy curl wheel

