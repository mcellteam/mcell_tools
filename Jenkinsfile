pipeline {
    agent any
    stages {
        stage('build') {
            steps {
                python 'run.py -qwe'
            }
        }
        stage('test') {
            steps {
                python 'run.py -r'
            }
        }
    }
}