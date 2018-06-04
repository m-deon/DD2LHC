import os

# *****************************
# Environment specific settings
# *****************************

# DO NOT use "DEBUG = True" in production environments
DEBUG = True

# DO NOT use Unsecure Secrets in production environments
# Generate a safe one with:
#     python -c "import os; print repr(os.urandom(24));"
SECRET_KEY = 'This is an UNSECURE Secret. CHANGE THIS for production environments.'

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///../app.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids a SQLAlchemy Warning

# Flask-Mail settings
# Note: Using Mailserver provided by EmmaTech (JCope) via Mailgun
MAIL_SERVER = 'smtp.mailgun.org'
MAIL_PORT = 587
MAIL_USE_SSL = False
MAIL_USE_TLS = True
MAIL_USERNAME = 'dmlimiter@mail.emmatech.us'
MAIL_PASSWORD = 'brandeismail'

# Sendgrid settings
SENDGRID_API_KEY='place-your-sendgrid-api-key-here'

# Flask-User settings
USER_APP_NAME = 'DM Limiter'
USER_EMAIL_SENDER_NAME = 'DM Limiter App'
USER_EMAIL_SENDER_EMAIL = 'dmlimiter@emmatech.us'

ADMINS = [
    '"Admin One" <admin1@gmail.com>',
    ]
