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
pip3 install -r requirements.txt
pip3 install "git+https://github.com/prostoLavr/
              async_lyceum_api.git"
```
### Run
```shell
# Setup postgresql
docker run --rm -it -e POSTGRES_PASSWORD="password" -d \
                 -p "5432:5432" --name "postgres" postgres:15.1

# Uncomment ot recreate db if it exists
# psql -h 0.0.0.0 -p 5432 -U postgres -c "DROP DATABASE db" 
psql -h 0.0.0.0 -p 5432 -U postgres -c "CREATE DATABASE db"

# See "async_lyceum_api --help" for more arguments
async_lyceum_api --web-port 8080
```

## Setup from source code in Python virtual environment
### Install packages
Install python3, python3-pip, python3-venv and docker. 
Instead docker you can install postgres 15.1 but docker is recommended.

### Clone source code
```shell
git clone https://github.com/prostoLavr/async_lyceum_api.git
```
### Initialize new virtual environment
```shell
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```
### Initialize development mode
Development mode is installing real-time updating python package.
It's useful to developers because you don't need building and
installing python package after edits.
```shell
pip3 install -e .  # <- This point in the end is important!
```

### Run native development mode
```shell
# Setup postgresql
docker run --rm -it -e POSTGRES_PASSWORD="password" -d \
                 -p "5432:5432" --name "postgres" postgres:15.1

# Uncomment ot recreate db if it exists
# psql -h 0.0.0.0 -p 5432 -U postgres -c "DROP DATABASE db" 
psql -h 0.0.0.0 -p 5432 -U postgres -c "CREATE DATABASE db"

# See "async_lyceum_api --help" for more arguments
async_lyceum_api --web-port 8080
```

## Setup from source code in Docker

### Install packages
Install python3-pip python3-venv, docker and docker-compose packages.

### Clone source code
```shell
git clone https://github.com/prostoLavr/async_lyceum_api.git
```
### Initialize new virtual environment
```shell
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

### Build python wheel package
This command will create python wheel file in dist directory.
```shell
python3 setup.py sdist bdist_wheel
```

### Build Docker image and up docker-compose services
```shell
docker build -t async-lyceum-api .  # <- This point in the end is important!
docker-compose up -d
```
