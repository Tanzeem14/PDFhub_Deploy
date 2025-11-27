properties([
  pipelineTriggers([]),
  durabilityHint('PERFORMANCE_OPTIMIZED')
])

pipeline {

    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: dind
    image: docker:dind
    securityContext:
      privileged: true
    command: ["dockerd-entrypoint.sh"]
    args:
      - "--host=tcp://0.0.0.0:2375"
      - "--insecure-registry=nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""
    volumeMounts:
    - mountPath: /home/jenkins/agent
      name: workspace-volume

  - name: sonar-scanner
    image: sonarsource/sonar-scanner-cli
    command: ["cat"]
    tty: true

  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["cat"]
    tty: true

  volumes:
  - name: workspace-volume
    emptyDir: {}
"""
        }
    }

    options {
        skipDefaultCheckout()
    }

    environment {
        DOCKER_IMAGE = "pdfhub"
        SONAR_TOKEN = "sqp_5c6bcf57fec846bce3562d1d777b633b4360c411"
        REGISTRY_HOST = "nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
        REGISTRY = "${REGISTRY_HOST}/2401067"
        NAMESPACE = "2401067"
    }

    stages {

        stage('Checkout Code') {
            steps {
                sh '''
                    rm -rf *
                    git clone https://github.com/Tanzeem14/PDFhub_Deploy.git .
                '''
                echo "✔ Source code cloned successfully"
            }
        }

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh """
                        docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} -t ${DOCKER_IMAGE}:latest .
                        docker image ls
                    """
                }
            }
        }

        stage('Run Tests & Generate Coverage') {
            steps {
                container('dind') {
                    sh """
                        docker run --rm \
                        -v $PWD:/workspace \
                        -w /workspace \
                        ${DOCKER_IMAGE}:latest \
                        pytest --maxfail=1 --disable-warnings --cov=. --cov-report=xml
                    """
                }
            }
        }

        // stage('SonarQube Analysis') {
        //     steps {
        //         container('sonar-scanner') {
        //             sh """
        //                 sonar-scanner \
        //                 -Dsonar.host.url=http://sonarqube-sonarqube.sonarqube.svc.cluster.local:9000 \
        //                 -Dsonar.token=${SONAR_TOKEN} \
        //                 -Dsonar.python.coverage.reportPaths=coverage.xml
        //             """
        //         }
        //     }
        // }
        stage('SonarQube Analysis') {
                    steps {
                        container('sonar-scanner') {
                            sh '''
                                sonar-scanner \
                                    -Dsonar.projectKey=2401067_PDFhub \
                                    -Dsonar.sources=. \
                                    -Dsonar.host.url=http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000 \
                                    -Dsonar.login=sqp_5c6bcf57fec846bce3562d1d777b633b4360c411
                            '''
                        }
                    }
                }

        stage('Login to Nexus Registry') {
            steps {
                container('dind') {
                    sh '''
                        docker login nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085 -u admin -p Changeme@2025
                    '''
                }
            }
        }

        stage('Tag & Push Docker Image to Nexus') {
            steps {
                container('dind') {
                    sh """
                        echo '📌 Tagging image...'
                        docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${REGISTRY}/${DOCKER_IMAGE}:${BUILD_NUMBER}

                        echo '📤 Pushing image to Nexus...'
                        docker push ${REGISTRY}/${DOCKER_IMAGE}:${BUILD_NUMBER}
                    """
                }
            }
        }

        stage('Create Namespace') {
            steps {
                container('kubectl') {
                    sh """
                        # 1. Create namespace if it doesn't exist
                        kubectl get namespace 2401067 || kubectl create namespace 2401067

                        # 2. Create Docker Registry Secret
                        kubectl create secret docker-registry nexus-secret \
                          --docker-server=${NEXUS_REGISTRY} \
                          --docker-username=admin \
                          --docker-password=Changeme@2025 \
                          --namespace=2401067 \
                          --dry-run=client -o yaml | kubectl apply -f -
                    """
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    dir('K8s-deployment') { 
                        sh """
                            # Update deployment.yaml to use the image with the current BUILD_NUMBER
                            # Ensure your deployment.yaml has 'image: .../client:latest' for this sed to work
                            sed -i "s|client:latest|${NEXUS_REGISTRY}/${REPO_NAME}/${IMAGE_NAME}:${BUILD_NUMBER}|g" deployment.yaml
                            
                            kubectl apply -f deployment.yaml
                            
                            # Give it a moment to start
                            sleep 5
                            kubectl get pods -n 2401067
                        """
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
