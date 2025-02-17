pipeline {
    agent any

    stages {
        stage('Run Python Script') {
            steps {
                script {
                    dir('D:\\AxiaManagerV1\\ReleaseSource') {
                        bat 'python generate_report.py "1.0.0.6"'
                    }
                }
            }
        }
    }
}
