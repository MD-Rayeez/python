pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                bat 'python hello.py'
            }
        }
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'devices.json', fingerprint: true
            }
        }
    }

    post {
        always {
            // Notify or clean up if needed
            echo 'Build completed!'
        }
    }
}
