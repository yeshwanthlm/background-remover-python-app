# Background Remover Python Application

A simple flask app to remove the background of an image with [Rembg](https://github.com/danielgatis/rembg)

## Run it locally:

```
pip install -r requirements.txt
python app.py
```

## Building Docker Image:

```
docker build -t flask-rmbg-app .
```

## Running Docker Image:

```
docker run -p 5100:5100 flask-rmbg-app
```

## Running Sonar Qube:

```
docker run -d --name sonar -p 9000:9000 sonarqube:lts-community
```


## Jenkins Pipeline Script:

```
pipeline {
    agent any
    environment {
        SCANNER_HOME = tool 'sonar-scanner'
    }
    stages {
        stage ("Clean workspace") {
            steps {
                cleanWs()
            }
        }
        stage ("Git checkout") {
            steps {
                git branch: 'main', url: 'https://github.com/yeshwanthlm/background-remover-python-app.git'
            }
        }
        stage("SonarQube Analysis") {
            steps {
                withSonarQubeEnv('sonar-server') {
                    sh ''' $SCANNER_HOME/bin/sonar-scanner -Dsonar.projectName=background-remover-python-app \
                    -Dsonar.projectKey=background-remover-python-app '''
                }
            }
        }
        stage("Quality Gate") {
            steps {
                script {
                    waitForQualityGate abortPipeline: false, credentialsId: 'Sonar-token'
                }
            }
        }
        stage('OWASP FS Scan') {
            steps {
                dependencyCheck additionalArguments: '--scan ./ --disableYarnAudit --disableNodeAudit', odcInstallation: 'DP-Check'
                dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
            }
        }
        stage ("Trivy File Scan") {
            steps {
                sh "trivy fs . > trivy.txt"
            }
        }
        stage ("Build Docker Image") {
            steps {
                sh "docker build -t background-remover-python-app ."
            }
        }
        stage ("Tag & Push to DockerHub") {
            steps {
                script {
                    withDockerRegistry(credentialsId: 'docker') {
                        sh "docker tag background-remover-python-app amonkincloud/background-remover-python-app:latest"
                        sh "docker push amonkincloud/background-remover-python-app:latest"
                    }
                }
            }
        }
        stage('Docker Scout Image') {
            steps {
                script {
                   withDockerRegistry(credentialsId: 'docker', toolName: 'docker') {
                       sh 'docker-scout quickview amonkincloud/background-remover-python-app:latest'
                       sh 'docker-scout cves amonkincloud/background-remover-python-app:latest'
                       sh 'docker-scout recommendations amonkincloud/background-remover-python-app:latest'
                   }
                }
            }
        }
        stage ("Deploy to Container") {
            steps {
                sh 'docker run -d --name background-remover-python-app -p 5100:5100 amonkincloud/background-remover-python-app:latest'
            }
        }
    }
    post {
    always {
        emailext attachLog: true,
            subject: "'${currentBuild.result}'",
            body: """
                <html>
                <body>
                    <div style="background-color: #FFA07A; padding: 10px; margin-bottom: 10px;">
                        <p style="color: white; font-weight: bold;">Project: ${env.JOB_NAME}</p>
                    </div>
                    <div style="background-color: #90EE90; padding: 10px; margin-bottom: 10px;">
                        <p style="color: white; font-weight: bold;">Build Number: ${env.BUILD_NUMBER}</p>
                    </div>
                    <div style="background-color: #87CEEB; padding: 10px; margin-bottom: 10px;">
                        <p style="color: white; font-weight: bold;">URL: ${env.BUILD_URL}</p>
                    </div>
                </body>
                </html>
            """,
            to: 'provide_your_Email_id_here',
            mimeType: 'text/html',
            attachmentsPattern: 'trivy.txt'
        }
    }
}

```
