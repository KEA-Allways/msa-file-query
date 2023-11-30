pipeline {
    agent any



    environment {
        
        
        //서버 정보
        ip = "54.147.162.65"
        username = "ubuntu"
        
        //스프링 서버 정보
        springname = "blog-query"
        port = "8086"
        
        //도커 정보
        imagename = "blog-query-img"
        dockerCredential = 'docker-access-token'
        dockerImage = ''
        tagname = "dev"
        
        //깃 정보
        giturl = 'https://github.com/KEA-Allways/msa-blog-query.git/'
        gitCredential = "github-access-token"
        branchname = "prod"
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

        // gradle build
        stage('Bulid Gradle') {
          steps {
            echo 'Bulid Gradle'
            dir ('.'){
                sh """
                ./gradlew clean build --exclude-task test
                """
            }
          }
          post {
            failure {
              error 'This pipeline stops here...'
            }
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

                sh "ssh -o StrictHostKeyChecking=no ${username}@${ip} 'docker ps -f name=${springname} -q | xargs --no-run-if-empty docker container stop'"
                sh "ssh -o StrictHostKeyChecking=no ${username}@${ip} 'docker container ls -a -fname=${springname} -q | xargs --no-run-if-empty docker container rm'"
                sh "ssh -o StrictHostKeyChecking=no ${username}@${ip} 'docker images -f reference=${imagename}:${tagname} -q | xargs --no-run-if-empty docker image rmi'"

                sh "ssh -o StrictHostKeyChecking=no ${username}@${ip} 'docker pull ${imagename}:${tagname}'"
                sh "ssh -o StrictHostKeyChecking=no ${username}@${ip} 'docker run -d -p 81:${port} -p ${port}:${port} --name ${springname} ${imagename}:${tagname}'"
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