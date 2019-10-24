pipeline {
    agent any
    
    stages {
        stage('checkout') {
            steps {
              sh 'git clone https://github.com/mcellteam/mcell_tools.git || exit 0'
              sh 'cd mcell_tools || exit 1; git checkout testing_infrastructure || exit 1; git pull || exit 1'
            }
        }
        stage('info') {
            steps {
              echo "Workspace location: ${env.WORKSPACE}"    
              sh 'ls -l mcell_tools'
            }
        }
        stage('clean') {
            steps {
              sh 'cd mcell_tools; python run.py --clean'
            }
        }
        stage('build') {
            steps {
              sh 'cd mcell_tools; python run.py --update --do-repos --do-build --do-bundle'
            }
        }
        stage('test') {
            steps {
              sh 'cd mcell_tools; python run.py --do-test'
            }
        }
    }
    post {  
      success {  
        mail subject: "PASSED: MCell test nr. ${env.BUILD_NUMBER} - ${env.NODE_NAME}", body: "Build: ${env.JOB_NAME} <br>Build Number: ${env.BUILD_NUMBER} <br> URL of build: ${env.BUILD_URL}", charset: 'UTF-8', from: '', mimeType: 'text/html', to: "mcelltester@gmail.com";  
      }  
      failure {  
        mail subject: "FAILED: MCell test nr. ${env.BUILD_NUMBER} - ${env.NODE_NAME}", body: "Build: ${env.JOB_NAME} <br>Build Number: ${env.BUILD_NUMBER} <br> URL of build: ${env.BUILD_URL}", charset: 'UTF-8', from: '', mimeType: 'text/html', to: "mcelltester@gmail.com";  
      }  
    }
}
