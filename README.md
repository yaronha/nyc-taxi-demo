# NYC Taxi Tutorial

[![Open In Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/yaronha/nyc-taxi-demo/blob/main/open-in-sagemaker.ipynb)

This project demonstrates a complete ML project and the development flow from initial exploration to continuous deployment at scale.
The example is based on a [Kaggle competition](https://www.kaggle.com/competitions/new-york-city-taxi-fare-prediction). 
It uses the public NYC Taxi dataset and its goal is to predict the correct trip fare. This example demonstrates the overall MLOps flow and is not intended to dive into the individual components or model.

- [**Overview**](#overview)
- [**Installation (local, GitHub codespaces, Sagemaker)**](#installation)

<a id="overview"></a>
## Overview 

ML application development and productization flow consists of the following steps (demonstrated through notebooks):

- [**Exploratory data analysis (EDA) and modeling**](./00-exploratory-data-analysis.ipynb).
- [**Data and model pipeline development**](./01-dataprep-train-test.ipynb) (data preparation, training, evaluation and so on).
- [**Application & serving pipeline development**](./02-serving-pipeline.ipynb) (intercept requests, process data, inference and so on).
- [**Scaling and automation**](./03-automation-monitoring.ipynb) (run at scale, hyper-parameter tuning, monitoring, pipeline automation and so on).
- Continuous operations (automated tests, CI/CD integration, upgrades, retraining, live ops and so on).

<img src="./images/project-dev-flow.png" alt="project-dev-flow"/><br>

You can find the python source code under [/src](./src) and the tests unset [/tests](./tests).

<a id="installation"></a>
## Installation

This project can run in different development environments:
1. Local computer (using PyCharm, VSCode, Jupyter, etc.)
2. Inside GitHub Codespaces 
3. Sagemaker studio and Studio Labs (free edition) or other managed Jupyter environments [![Open In Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/yaronha/nyc-taxi-demo/blob/main/open-in-sagemaker.ipynb)


### Install the code and mlrun client 

To get started, fork this repo into your GitHub account and clone it into your development environment.

To install the package dependencies (not required in GitHub codespaces) use:
 
    make install-requirements
    
If you prefer to use Conda or work in **Sagemaker** use this instead (to create and configure a conda env):

    make conda-env

> Make sure you open the notebooks and select the `mlrun` conda environment 
 
### Install or connect to MLRun service/cluster

The MLRun service and computation can run locally (minimal setup) or over a remote Kubernetes environment.

If your development environment support docker and have enough CPU resources run:

    make mlrun-docker
    
> MLRun UI can be viewed in: http://localhost:8060
    
If your environment is minimal or you are in Sagemaker run mlrun as a process (no UI):

    [conda activate mlrun &&] make mlrun-api
 
For MLRun to run properly you should set your client environment, this is not required when using **codespaces**, the mlrun **conda** environment, or **iguazio** managed notebooks.

Your environment should include `MLRUN_ENV_FILE=<absolute path to the ./mlrun.env file> ` (point to the mlrun .env file in this repo), see [mlrun client setup](https://docs.mlrun.org/en/latest/install/remote.html) instructions for details.  
     
> Note: You can also use a remote MLRun service (over Kubernetes), instead of starting a local mlrun, 
> edit the [mlrun.env](./mlrun.env) and specify its address and credentials  
