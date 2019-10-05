node {
    stage('info') {
        steps {
            sh 'pwd'
        }
    }
    stage('build') {
        steps {
            sh 'python run.py -qwe'
        }
    }
    stage('test') {
        steps {
            sh 'python run.py -r'
        }
    }
}
