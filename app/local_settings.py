# encoding: utf-8
import os

# *****************************
# Environment specific settings
# *****************************

# DO NOT use "DEBUG = True" in production environments
DEBUG = True

# DO NOT use Unsecure Secrets in production environments
# Generate a safe one with:
#     python -c "import os; print repr(os.urandom(24));"
SECRET_KEY = '566287894cf05b610f4c52dfcd2f0974d538db9059ae37b3'

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///../app.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids a SQLAlchemy Warning

# Flask-Mail settings
# Note: Using Mailserver provided by EmmaTech (JCope) via Mailgun
MAIL_SERVER = os.getenv('DML_MAIL_SERVER','smtp.mailgun.org')
MAIL_PORT = 587
MAIL_USE_SSL = False
MAIL_USE_TLS = True

MAIL_USERNAME = os.getenv('DML_MAIL_USER','')
MAIL_PASSWORD = os.getenv('DML_MAIL_PSWD','')
MAIL_DEFAULT_SENDER = os.getenv('DML_MAIL_SENDER','app@dmlimiter.com')

# Flask-User settings
USER_APP_NAME = 'DM Limiter'
USER_EMAIL_SENDER_NAME = 'DM Limiter App'
USER_EMAIL_SENDER_EMAIL = 'app@dmlimiter.com'

ADMINS = [
    '"Administrator" <admin@dmlimiter.com>',
    ]
