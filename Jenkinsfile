#!/usr/bin/env groovy
pipeline {
    agent any
    environment {
        AZURE_REGISTRY_CREDS = credentials('theircregistry1')
    }
    stages {
        stage('Build Stage') {
            when {
                expression {
                  env.GIT_BRANCH == "origin/master"
                }
            }
            steps {
                echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
                //checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'b1a075ef-ec65-4c28-994c-9a64f6a8dfb1', url: 'https://github.com/theirc/tashbeek']]])
                sh "docker --version"
                sh "docker build -t theircregistry1.azurecr.io/tashbeek:stage ."
            }
        }
        stage('Deploy Stage') {
            when {
                expression {
                  env.GIT_BRANCH == "origin/master" && (currentBuild.result == null || currentBuild.result == 'SUCCESS')
                }
            }
            steps {
                sh "docker login theircregistry1.azurecr.io --username ${env.AZURE_REGISTRY_CREDS_USR} --password ${env.AZURE_REGISTRY_CREDS_PSW}"
                sh "docker push theircregistry1.azurecr.io/tashbeek:stage"
            }
        }
        stage('Clean-up Stage') {
            when {
                expression {
                env.GIT_BRANCH == "origin/master" && (currentBuild.result == null || currentBuild.result == 'SUCCESS')
              }
            }
            steps {
                sh "docker rmi theircregistry1.azurecr.io/tashbeek:stage"
            }
        }
        stage('Build Prod') {
            when {
                expression {
                  env.GIT_BRANCH == "origin/master"
                }
            }
            steps {
                echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
                sh "docker --version"
                sh "docker build -t theircregistry1.azurecr.io/tashbeek:latest ."
            }
        }
        stage('Deploy Prod') {
            when {
                expression {
                    env.GIT_BRANCH == "origin/master" && (currentBuild.result == null || currentBuild.result == 'SUCCESS')
                }
            }
            steps {
                sh "docker login theircregistry1.azurecr.io --username ${env.AZURE_REGISTRY_CREDS_USR} --password ${env.AZURE_REGISTRY_CREDS_PSW}"
                sh "docker push theircregistry1.azurecr.io/tashbeek:latest"
            }
        }
        stage('Clean-up Prod') {
            when {
                expression {
                    env.GIT_BRANCH == "origin/master" && (currentBuild.result == null || currentBuild.result == 'SUCCESS')
                }
            }
            steps {
                sh "docker rmi theircregistry1.azurecr.io/tashbeek:latest"
            }
        }
    }
}
