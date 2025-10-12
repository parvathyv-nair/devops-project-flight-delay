pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "vanshikakoshti/flight-delay-app:latest"
    }

    stages {
        stage('Checkout Code') {
            steps {
                // Explicitly checkout main branch
                git branch: 'main', url: 'https://github.com/parvathyv-nair/devops-project-flight-delay.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build Docker image
                    docker.build(DOCKER_IMAGE)
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    // Push Docker image to Docker Hub
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-hub-credentials') {
                        docker.image(DOCKER_IMAGE).push()
                    }
                }
            }
        }

        stage('Deploy Container') {
            steps {
                sh """
                # Stop previous container if exists
                docker stop flight-delay-app || true
                docker rm flight-delay-app || true

                # Run the new container
                docker run -d -p 5000:5000 --name flight-delay-app ${DOCKER_IMAGE}
                """
            }
        }
    }

    post {
        success {
            echo "Pipeline finished successfully! App should be running on http://<VM-IP>:5000"
        }
        failure {
            echo "Pipeline failed. Check logs for errors."
        }
    }
}
