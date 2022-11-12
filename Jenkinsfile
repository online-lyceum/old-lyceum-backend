#!groovy

properties([disableConcurrentBuilds()])

pipeline {
    agent any
    options {
        buildDiscarder(logRotator(numToKeepStr: '5', artifactNumToKeepStr: '5'))
        timestamps()
    }
    triggers { pollSCM('* * * * *') }
    stages {
        stage("Create a venv") {
            when { not { expression { return not fileExists ('./venv') } } }
            steps {
                sh 'python3 -m venv ./venv'
                sh './venv/bin/python3 -m pip install -r requirements.txt'
            }
        }
        stage("Build image") {
            steps {
                sh 'rm -rf dist'
                sh './venv/bin/python3 setup.py sdist bdist_wheel'
                sh 'docker build -t async-lyceum-api .'
            }
        }
        stage("Run images") {
            steps {
                sh 'docker-compose up -d'
            }
        }
    }
}
