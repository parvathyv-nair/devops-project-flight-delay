pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "vanshikakoshti/flight-delay-app:latest"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git 'https://github.com/parvathyv-nair/devops-project-flight-delay.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build(DOCKER_IMAGE)
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-hub-credentials') {
                        docker.image(DOCKER_IMAGE).push()
                    }
                }
            }
        }

        stage('Deploy Container') {
            steps {
                sh """
                docker stop flight-delay-app || true
                docker rm flight-delay-app || true
                docker run -d -p 5000:5000 --name flight-delay-app ${DOCKER_IMAGE}
                """
            }
        }
    }
}
