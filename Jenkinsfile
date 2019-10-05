node {
    stage('info') {
        sh 'pwd'
    }
    stage('clean') {
        sh 'python run.py -c'
    }
    stage('build') {
        sh 'python run.py -qwe'
    }
    stage('test') {
        sh 'python run.py -r'
    }
}
