// pipeline {
//     agent any
//     stages {
//         stage('Setup Environment') {
//             steps {
//                 // Verify Python version and ensure pip is installed
//                 sh '''
//                 echo "Python Version:"
//                 python3 --version
//                 echo "Pip Version:"
//                 python3 -m pip --version
//                 '''
//             }
//         }
//         stage('Install Dependencies') {
//             steps {
//                 // Install PyMySQL using pip
//                 sh '''
//                 echo "Installing PyMySQL..."
//                 python3 -m pip install --upgrade pip
//                 python3 -m pip install PyMySQL
//                 '''
//             }
//         }
//         stage('Verify Installation') {
//             steps {
//                 // Check if PyMySQL is properly installed
//                 sh '''
//                 echo "Verifying PyMySQL installation..."
//                 python3 -m pip show PyMySQL
//                 python3 -c "import pymysql; print('PyMySQL Version:', pymysql.__version__)"
//                 '''
//             }
//         }
//         stage('Run Script') {
//             steps {
//                 // Execute the Python script
//                 sh '''
//                 echo "Running hello.py..."
//                 python3 hello.py
//                 '''
//             }
//         }
//     }
//     post {
//         always {
//             // Clean up (optional)
//             echo 'Pipeline finished.'
//         }
//     }
// }

pipeline {
    agent any
    stages {
        stage('Run Script') {
            steps {
                // Execute the Python script
                sh '''
                echo "Running hello.py..."
                python3 hello.py
                '''
            }
        }
    }
    post {
        always {
            echo 'Pipeline finished.'
        }
    }
}


// pipeline {
//     agent any
    
//     stages {
//         stage('Build') {
//             steps {
//                 sh 'python3 hello.py'
//             }
//         }
//         stage('Archive') {
//             steps {
//                 archiveArtifacts artifacts: 'devices.json', fingerprint: true
//             }
//         }
//     }

//     post {
//         always {
//             // Notify or clean up if needed
//             echo 'Build completed!'
//         }
//     }
// }