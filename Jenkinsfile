pipeline {
    agent any



    environment {

        //서버 정보
        ip = "3.86.230.148"
        username = "ubuntu"
        
        //서버 정보
        servername = "file-query"
        port = "8088"
        
        //도커 정보
        imagename = "file-query-img"
        dockerCredential = 'docker-access-token'
        dockerImage = ''
        tagname = "dev"
        
        //깃 정보
        giturl = 'https://github.com/KEA-Allways/msa-file-query.git/'
        gitCredential = "github-access-token"
        branchname = "dev"
    }

    stages {
        // git에서 repository clone
        stage('Prepare') {
          steps {
            echo 'Clonning Repository'
              git url: giturl,
              branch: branchname,
              credentialsId: gitCredential
            }
            post {
             success { 
               echo 'Successfully Cloned Repository'
             }
           	 failure {
               error 'This pipeline stops here...'
             }
          }
        }


         stage('Create env file') {
            steps {
                dir(".") {

                    sh '''
                        touch .env
                        echo 'MONGO_DB_URL=mongodb://root:0707@172.16.210.121:27017/?authMechanism=DEFAULT/' >> .env
                        echo 'REST_API_KEY=5a2a4e45ffeb910b796bec78b8641b9e' >> .env
                        echo 'AWS_REGION=us-east-1' >> .env
                        echo 'S3_BUCKET_NAME=unv-gcu-allways-bucket' >> .env
                        echo 'AWS_ACCESS_KEY_ID=AKIAZFEQRMP3SU6GZS4V' >> .env
                        echo 'AWS_SECRET_ACCESS_KEY=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' >> .env
                    '''
                }
            }

            post {
            failure {
              error 'This pipeline stops here...'
            }
          }

        // docker build
        stage('Bulid Docker') {
          steps {
            echo 'Bulid Docker'
            script {
                imagename = "jmk7117/${imagename}"
                dockerImage = docker.build imagename
            }
          }
          post {
            failure {
              error 'This pipeline stops here...'
            }
          }
        }

        // docker push
        stage('Push Docker') {
          steps {
            echo 'Push Docker'
            script {
                docker.withRegistry( '', dockerCredential) {
                    dockerImage.push("dev")
                }
            }
          }
          post {
            failure {
              error 'This pipeline stops here...'
            }
          }
        }
        
        stage('Run Container on Dev Server') {
          steps {
            echo 'Run Container on Dev Server'
            
            sshagent(['ec2-ssh']) {


                sh 'ssh -o StrictHostKeyChecking=no ${username}@${ip} "whoami"'

                sh "ssh -o StrictHostKeyChecking=no ${username}@${ip} 'docker ps -f name=${servername} -q | xargs --no-run-if-empty docker container stop'"
                sh "ssh -o StrictHostKeyChecking=no ${username}@${ip} 'docker container ls -a -fname=${servername} -q | xargs --no-run-if-empty docker container rm'"
                sh "ssh -o StrictHostKeyChecking=no ${username}@${ip} 'docker images -f reference=${imagename}:${tagname} -q | xargs --no-run-if-empty docker image rmi'"

                sh "ssh -o StrictHostKeyChecking=no ${username}@${ip} 'docker pull ${imagename}:${tagname}'"
                sh "ssh -o StrictHostKeyChecking=no ${username}@${ip} 'docker run -d -p 80:${port} -p ${port}:${port} --name ${servername} ${imagename}:${tagname}'"
            }
          }

          post {
                  success {
                      slackSend (
                          channel: '#jenkins',
                          color: '#00FF00',
                          message: "SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})"


                      )
                  }
                  failure {
                      slackSend (
                          channel: '#jenkins',
                          color: '#FF0000',
                          message: "FAIL: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})"
                      )
                  }
              }
          
        }
    }
}