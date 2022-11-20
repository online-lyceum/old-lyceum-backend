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
        stage("Build image") {
            steps {
                sh 'docker build -t async-lyceum-api .'
            }
        }
        stage("Run images") {
            steps {
                sh 'docker-compose up -d'
                sh 'sleep 5'
                sh 'docker-compose exec async_lyceum_api init_models'
            }
        }
    }
}
