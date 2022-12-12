#!groovy

pipeline {
    agent any
    stages {
        stage("Build image") {
            steps {
                sh 'docker build -t time_api:${JOB_NAME} .'
            }
        }
        stage("Run images") {
            steps {
                sh 'docker-compose up -d'
                sh 'sleep 5'
                sh 'docker-compose exec -d time_api_${JOB_NAME} init_models'
            }
        }
    }
}
