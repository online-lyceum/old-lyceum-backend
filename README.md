# Asynchronous lyceum API
## About
Lyceum is a project to provide timetables for educational establishments.
A main feature is a mobile application.
To start use it in your educational establishment please write us.

Our contacts will be here later.

This project is a part of a microservice architecture.
The API afford http requests to read and write objects data.

Other repositories will be here later too.



## Setup from GitHub (Without development mode)
### Install packages
Install python3-pip and python3-venv packages.

### Create venv and install package
```shell
python3 -m venv venv
source ./venv/bin/activate
pip3 install setuptools
pip3 install "git+https://github.com/prostoLavr/
              async_lyceum_api.git"
```

## Setup from source code
### Install packages
Install python3-pip and python3-venv packages.

### Initialize new virtual environment
```shell
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

### Initialize development mode
WARNING: notify for point in the command end.
```shell
pip3 install -e .
```

### Run development mode
Development mode is installing real-time updating python package.
It's useful to developers because you don't need building and
installing python package after edits.
```shell
async_lyceum_api 
```
or
```shell
async_lyceum_api --host 127.0.0.1 --port 8080
```

### Build python wheel package
This command will create python wheel file in dist directory.
```shell
python3 setup.py sdist bdist_wheel
```


### Install python wheel package
WARNING: This command will break the development mode.
Go to "Initialize development mode" step to start the development mode again.
```shell
pip3 install ./dist/async_lyceum_api-{VERSION}-py3-none-any.whl
```

### Run
```shell
async_lyceum_api
```
Or
```shell
async_lyceum_api --host 127.0.0.1 --port 8080
```