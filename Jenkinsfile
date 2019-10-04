pipeline {
    agent any
    stages {
        stage('build') {
            steps {
                pwd
                sh 'python run.py -qwe'
            }
        }
        stage('test') {
            steps {
                sh 'python run.py -r'
            }
        }
    }
}