pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code from GitHub'
                checkout scm
            }
        }

        stage('Validate Python') {
            steps {
                echo 'Validating Python syntax'
                sh 'python3 -m py_compile backend/app.py'
            }
        }

        stage('Build Docker Images') {
            steps {
                echo 'Building Docker images'
                sh 'docker compose build'
            }
        }

        stage('Deploy Application') {
            steps {
                echo 'Deploying application with Docker Compose'
                sh 'docker compose up -d'
            }
        }

        stage('Health Check') {
            steps {
                echo 'Checking backend health endpoint'
                sh 'curl --fail --retry 5 --retry-delay 2 http://host.docker.internal:8081/health'
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD pipeline failed. Check the console output.'
        }
    }
}
