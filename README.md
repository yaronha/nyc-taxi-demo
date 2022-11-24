# NYC Taxi Tutorial

This project demonstrates how to build an ML application and use MLOps to operationalize it.

## Getting started

After you cloned the repository install the required packages using:
 
    make install-requirements

Configure MLRun environment file path (not required in GitHub codespaces):

    export MLRUN_ENV_FILE=./mlrun.env

To start a local version of MLRun service (using Docker compose) type:

    make start-mlrun
    
> Note: You can also use a remote MLRun service (over Kubernetes), instead of starting a local mlrun, 
> edit the [mlrun.env](./mlrun.env) and specify its address and credentials  

## Tutorial notebooks 

The project contains four notebooks, in the following order:

- [**Exploratory Data Analysis**](./00-exploratory-data-analysis.ipynb)
- [**Data preparation, training and evaluating a model**](./01-dataprep-train-test.ipynb)
- [**Application Serving Pipeline**](./02-serving-pipeline.ipynb)
- [**Pipeline Automation and Model Monitoring**](./03-automation-monitoring.ipynb)

You can find the python source code under [/src](./src)
