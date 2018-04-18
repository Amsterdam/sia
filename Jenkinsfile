#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block();
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#stadinbalans', color: 'danger'

        throw t;
    }
    finally {
        if (tearDown) {
            tearDown();
        }
    }
}


node {

    stage("Checkout") {
        checkout scm
    }

    stage("Build dockers") {
        tryStep "build", {
            def frontend = docker.build("build.app.amsterdam.nl:5000/cto/vaarwatermeldingen_frontend:${env.BUILD_NUMBER}", "frontend")
                frontend.push()
                frontend.push("acceptance")

            def classifier = docker.build("build.app.amsterdam.nl:5000/cto/vaarwatermeldingen_classifier:${env.BUILD_NUMBER}", "classifier")
                classifier.push()
                classifier.push("acceptance")

            def api = docker.build("build.app.amsterdam.nl:5000/cto/vaarwatermeldingen:${env.BUILD_NUMBER}", ".")
                api.push()
                api.push("acceptance")
        }
    }
}

String BRANCH = "${env.BRANCH_NAME}"

if (BRANCH == "master") {

    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
                def image = docker.image("build.app.amsterdam.nl:5000/cto/vaarwatermeldingen:${env.BUILD_NUMBER}")
                image.pull()
                image.push("acceptance")
            }
        }
    }

    node {
        stage("Deploy to ACC") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-vaarwatermeldingen.yml'],
                ]
            }
        }
    }

    stage('Waiting for approval') {
        slackSend channel: '#stadinbalans', color: 'warning', message: 'Vaarwater meldingen is waiting for Production Release - please confirm'
        input "Deploy to Production?"
    }

    node {
        stage('Push production image') {
            tryStep "image tagging", {
                def api = docker.image("build.app.amsterdam.nl:5000/cto/vaarwatermeldingen:${env.BUILD_NUMBER}")
                def analyzer = docker.image("build.app.amsterdam.nl:5000/cto/vaarwatermeldingen_classifier:${env.BUILD_NUMBER}")
                def importer = docker.image("build.app.amsterdam.nl:5000/cto/vaarwatermeldingen_frontend:${env.BUILD_NUMBER}")

                frontend.push("production")
                frontend.push("latest")

                classifier.push("production")
                classifier.push("latest")

                api.push("production")
                api.push("latest")
            }
        }
    }

    node {
        stage("Deploy") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: 'production'],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-vaarwatermeldingen.yml'],
                ]
            }
        }
    }
}
