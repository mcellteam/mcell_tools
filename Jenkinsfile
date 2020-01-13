pipeline {
    agent { label "${env.NODE_LABEL}" }
    
    stages {
        stage("checkout") {
            steps {
              sh "git clone https://github.com/mcellteam/mcell_tools.git || exit 0"
              sh "cd mcell_tools || exit 1; git checkout testing_infrastructure || exit 1; git pull || exit 1"
            }
        }
        stage("info") {
            steps {
              echo "Workspace location: ${env.WORKSPACE}"    
              sh "ls -l mcell_tools"
            }
        }
        stage("clean") {
            steps {
              // need to call bash like this because Windows has parentheses .. (x86) in PATH and sh does not handle it
              sh '''#!/bin/bash -xe
                    export PATH=$PATH:/usr/local/bin; cd mcell_tools; python3 run.py --clean
                 '''
            }
        }
        stage("build") {
            steps {
              // /usr/local/opt/bison/bin is required for MacOs because an older version is the default there 
              sh '''#!/bin/bash -xe
                    export PATH=/usr/local/opt/bison/bin:$PATH:/usr/local/bin; cd mcell_tools; python3 run.py --branch ${TESTED_BRANCH} --update --do-repos --do-build --do-bundle ${EXTRA_BUILD_ARGS}
                 '''
            }
        }
        stage("test") {
            steps {
              sh '''#!/bin/bash -xe
                    export PATH=$PATH:/usr/local/bin; cd mcell_tools; python3 run.py --do-test --store-build
                 '''
            }
        }
    }
    post {  
      success {  
        mail subject: "PASSED: MCell test nr. ${env.BUILD_NUMBER} - ${env.NODE_NAME} - ${env.TESTED_BRANCH}", body: "Build: ${env.JOB_NAME} <br>Build Number: ${env.BUILD_NUMBER} <br> URL of build: ${env.BUILD_URL} <br> Branch: ${env.TESTED_BRANCH}", charset: 'UTF-8', from: "mcelltester@gmail.com", mimeType: 'text/html', to: "mcelltester@gmail.com";  
      }  
      failure {  
        mail subject: "FAILED: MCell test nr. ${env.BUILD_NUMBER} - ${env.NODE_NAME} - ${env.TESTED_BRANCH}", body: "Build: ${env.JOB_NAME} <br>Build Number: ${env.BUILD_NUMBER} <br> URL of build: ${env.BUILD_URL} <br> Branch: ${env.TESTED_BRANCH}", charset: 'UTF-8', from: "mcelltester@gmail.com", mimeType: 'text/html', to: "mcelltester@gmail.com";  
      }  
    }
}
