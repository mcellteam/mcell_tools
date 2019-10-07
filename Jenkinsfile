node {
    stage('checkout') {
        sh 'git clone https://github.com/mcellteam/mcell_tools.git || exit 0'
        sh 'cd mcell_tools || exit 1; git checkout testing_infrastructure || exit 1; git pull || exit 1'
    }
    stage('info') {
        echo "Workspace location: ${env.WORKSPACE}"    
        sh 'ls -l mcell_tools'
    }
    stage('clean') {
        sh 'cd mcell_tools; python run.py -c'
    }
    stage('build') {
        sh 'cd mcell_tools; python run.py -qwe'
    }
    stage('test') {
        sh 'cd mcell_tools; python run.py -r'
    }
}
