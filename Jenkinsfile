#!groovy

pipeline {
    agent any
    stages {
        stage("Build and up") {
            steps {
                sh 'docker-compose up -d --build --remove-orphans'
            }
        }
        stage("DB Migrate") {
            steps {
                sh 'docker-compose exec -d api init_models'
            }
        }
    }
}
