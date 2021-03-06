# EE_Python

## Run the project

### Using Docker

Run the container with the following cmd :
```docker run -it --name "geemap" -p 8888:8888 -p 6006:6006 -v C:\dev\Github_code\EE_Python\app:/geemap/data bkavlak/geemap:latest bash```

If you haven't pulled the geemap image yet, the download will occur the first time you run the command (might take a few minutes/hours depending on your internet connexion).

Once the container is up and running, it's CLI should be accessible through the current terminal. If you are using Docker Desktop, you can also access the CLI through the dedicated button on the "Containers / Apps" window.

### Using Conda

(If you haven't installed Conda on your system, please follow these instructions : https://developers.google.com/earth-engine/guides/python_install-conda#install_conda)7

Install on Windows :
```powershell -command "Invoke-WebRequest -Uri https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe -OutFile ~\miniconda.exe"```

```start /B /WAIT %UserProfile%\miniconda.exe /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /S /D=%UserProfile%\miniconda3```

```del %UserProfile%\miniconda.exe```

Test Miniconda install :
```%UserProfile%\miniconda3\condabin\activate```
```conda --help```

Add Miniconda to environment variables :
```setx Path "%Path%%UserProfile%\miniconda3\condabin;"```

First of all, make sure the "conda-forge" channel is added to your current conda configuration (it you appear in the channels list when typing the following: ```conda config --show channels```)

If it is not added yet, add it using the following command :
```conda config --add channels conda-forge```

Then do the same thing for the "roulbac" channel.

conda create --name ee
conda activate ee
conda install pip
conda install conda-build

https://veillecarto2-0.fr/2019/12/11/tutorial-create-an-anaconda-environment-for-pyqgis-development/

To install the conda env using the requirements.txt file type :
```conda create --name ee --file requirements.txt```

Update the requirements.txt file : after installing new packages, you can re-generate the requirements.txt file using :
```conda list -e > requirements.txt```

To run the project using conda type :
```conda activate ee```

To run the Auth script you'll need to have the Google Cloud CLI installed : https://cloud.google.com/sdk/docs/install

## Sources

Docker project taken from -> https://github.com/bkavlak/geemap_docker