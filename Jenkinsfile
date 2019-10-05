node {
    stage('info') {
        sh 'pwd'
    }
    stage('clean') {
	sh 'rm -r work'
    }
    stage('build') {
        sh 'python run.py -qwe'
    }
    stage('test') {
        sh 'python run.py -r'
    }
}
