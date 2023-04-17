#!groovy

pipeline {
    agent any
    stages {
        stage("Build and up") {
            steps {
                sh 'docker-compose -f docker-compose.prod.yml up-d --build --remove-orphans'
            }
        }
        stage("DB Migrate") {
            steps {
                sh 'docker-compose -f docker-compose.prod.yml exec -d api init_models'
            }
        }
    }
}
