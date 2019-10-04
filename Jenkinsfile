pipeline {
  agent any
  stages {
    stage('build') {
      steps {
        script {
          python run.py -qwe
        }

      }
    }
    stage('test') {
      steps {
        script {
          python run.py -r
        }

      }
    }
  }
}