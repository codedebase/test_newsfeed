pipeline {
    agent any

    environment {
        OPENAI_API_KEY = credentials('OPENAI_API_KEY')
        SMTP_USER = credentials('SMTP_USER')
        SMTP_PASS = credentials('SMTP_PASS')
        RECIPIENT_EMAIL = credentials('RECIPIENT_EMAIL')
    }

    triggers {
        // 每日 NY 6AM = UTC 10AM
        cron('0 10 * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set up Python') {
            steps {
                sh '''
                  python3 -m venv venv
                  . venv/bin/activate
                  pip install --upgrade pip
                  pip install -r requirements.txt
                '''
            }
        }

        stage('Run script') {
            steps {
                sh '''
                  . venv/bin/activate
                  python news_email_agent.py
                '''
            }
        }
    }
}
