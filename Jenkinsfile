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
                sh 'docker-compose up -d --remove-orphans'
                sh 'sleep 8'
                sh 'docker-compose exec api init_models'
            }
        }
    }
}
