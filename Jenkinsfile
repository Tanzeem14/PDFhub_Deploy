properties([
  pipelineTriggers([]),
  durabilityHint('PERFORMANCE_OPTIMIZED')
])

pipeline {
    agent any

    options {
        skipDefaultCheckout()   // disable default problematic checkout
    }

    environment {
        DOCKER_IMAGE = "pdfhub"
        SONAR_TOKEN = "sqp_5c6bcf57fec846bce3562d1d777b633b4360c411"  // replace later with Jenkins credentials
        REGISTRY = "nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085/2401067"
        NAMESPACE = "2401067"
    }

    stages {

        stage('Checkout Code') {
            steps {
                sh '''
                    rm -rf *
                    git clone https://github.com/Tanzeem14/PDFhub_Deploy.git .
                '''
                echo "✔ PDFhub source code cloned successfully"
            }
        }

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh '''
                        docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} -t ${DOCKER_IMAGE}:latest .
                        docker image ls
                    '''
                }
            }
        }

        stage('Run Tests & Generate Coverage') {
            steps {
                container('dind') {
                    sh '''
                        docker run --rm \
                        -v $PWD:/workspace \
                        -w /workspace \
                        ${DOCKER_IMAGE}:latest \
                        pytest --maxfail=1 --disable-warnings --cov=. --cov-report=xml
                    '''
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    sh """
                        sonar-scanner \
                            -Dsonar.host.url=http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000 \
                            -Dsonar.login=${SONAR_TOKEN}
                    """
                }
            }
        }

        stage('Login to Nexus Docker Registry') {
            steps {
                container('dind') {
                    sh """
                        docker login ${REGISTRY} -u admin -p Changeme@2025
                    """
                }
            }
        }

        stage('Tag & Push Image to Nexus') {
            steps {
                container('dind') {
                    sh """
                        docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${REGISTRY}/${DOCKER_IMAGE}:${BUILD_NUMBER}
                        docker push ${REGISTRY}/${DOCKER_IMAGE}:${BUILD_NUMBER}
                    """
                }
            }
        }

        stage('Deploy PDFhub to Kubernetes') {
            steps {
                container('kubectl') {
                    script {
                        dir('k8s-deployment') {
                            sh """
                                kubectl apply -f deployment.yaml
                                kubectl set image deployment/pdfhub-app pdfhub-container=${REGISTRY}/${DOCKER_IMAGE}:${BUILD_NUMBER} -n ${NAMESPACE}
                                kubectl rollout status deployment/pdfhub-app -n ${NAMESPACE}
                            """
                        }
                    }
                }
            }
        }
    }

    post {
        success { echo "🎉 PDFhub CI/CD Pipeline completed successfully!" }
        failure { echo "❌ PDFhub CI/CD Pipeline failed" }
        always  { echo "🔄 Pipeline finished" }
    }
}
