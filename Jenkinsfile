pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'pdfhub-web'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        REGISTRY_URL = "http://localhost:8084"
        K8S_DEPLOYMENT = "pdfhub-app"
        K8S_NAMESPACE = "default"
        CONTAINER_NAME = "pdfhub-container"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Cloning source code..."
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo "Running tests (if configured)..."
                // Add your test commands here
                // sh 'pytest tests/'
            }
        }

        stage('Push to Nexus Docker Registry') {
            steps {
                echo "Pushing Docker images to Nexus Registry..."
                script {
                    docker.withRegistry("${REGISTRY_URL}", 'nexus-docker-creds') {
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                        docker.image("${DOCKER_IMAGE}:latest").push()
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo "Deploying to Kubernetes..."
                script {

                    // Update existing deployment
                    sh """
                    kubectl set image deployment/${K8S_DEPLOYMENT} \
                        ${CONTAINER_NAME}=${DOCKER_IMAGE}:${DOCKER_TAG} \
                        -n ${K8S_NAMESPACE} || true
                    """

                    // Ensure deployment exists
                    sh """
                    kubectl apply -f k8s/deployment.yaml -n ${K8S_NAMESPACE}
                    """

                    // Apply service if not created
                    sh """
                    kubectl apply -f k8s/service.yaml -n ${K8S_NAMESPACE}
                    """

                    // Check rollout
                    sh """
                    kubectl rollout status deployment/${K8S_DEPLOYMENT} -n ${K8S_NAMESPACE}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "PDFHUB CI/CD Pipeline completed successfully! 🎉"
        }
        failure {
            echo "PDFHUB CI/CD Pipeline FAILED ❌"
        }
        always {
            echo "Cleaning up..."
            // Optional cleanup
            // sh "docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true"
        }
    }
}
