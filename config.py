import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'sql', 'migrate_repo')

WTF_CSRF_ENABLED = True
SECRET_KEY = 'bibliotheque pierre pactet'
SQLALCHEMY_TRACK_MODIFICATIONS = True

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['odile.benassy@u-psud.fr']

LDAP_PROVIDER_URL = 'ldap://ldap.u-psud.fr:389'
LDAP_PROTOCOL_VERSION = 3

# Database
MYSQL_DATABASE_USER = 'fluser'
MYSQL_DATABASE_PASSWORD = 'flpass'
MYSQL_DATABASE_DB = 'flcoll'
MYSQL_DATABASE_HOST = 'localhost'
