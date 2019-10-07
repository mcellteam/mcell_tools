node {
    stage('info') {
      steps {      
        echo "Workspace location: ${env.WORKSPACE}"    
        sh 'ls -l'
      }
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
