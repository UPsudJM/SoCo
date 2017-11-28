# -*- coding: utf-8 -*-
# available languages
LANGUAGES = {'en': 'English', 'fr': 'Français'}
import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'psql', 'migrate_repo')

WTF_CSRF_ENABLED = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = 'my secret key'
#from secret import SECRET_KEY

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DOMAIN = 'u-psud.fr'

# administrator list
ADMINS = []         # your email here
#from secret import ADMINS

# User authentication
USE_PWHASH = True
USE_LDAP = False
#LDAP_PROVIDER_URL = 'your.ldap.server'
#LDAP_SEARCH_BASE = 'dc=xyz, dc=tuv'
#LDAP_USER_PATT = 'uid=%s,ou=people,dc=xuz,dc=tuv'

# Database and other secrets
PGSQL_DATABASE_DB = 'soco'
PGSQL_DATABASE_HOST = 'localhost'
PGSQL_DATABASE_USER = 'myuser'
PGSQL_DATABASE_PASSWORD = 'mypass'
#from secret import PGSQL_DATABASE_USER, PGSQL_DATABASE_PASSWORD

DB_ENGINE = 'postgresql'

# Same, with MySQL
MYSQL_DATABASE_DB = 'soco'
MYSQL_DATABASE_HOST = 'localhost'
MYSQL_DATABASE_USER = 'myuser'
MYSQL_DATABASE_PASSWORD = 'mypass'
#from secret import MYSQL_DATABASE_USER, MYSQL_DATABASE_PASSWORD

#DB_ENGINE = 'mysql'

# available languages
LANGUAGES = {
    'en': 'English',
    'fr': 'Français'
    }
BABEL_DEFAULT_LOCALE = 'fr'

# logo upload
LOGO_FOLDER=basedir + '/soco/static/logos/'
LOGO_URL_REL='logos/'
LOGO_EXTENSIONS=['png', 'jpeg', 'jpg', 'gif']
LOGO_DEFAULT='soco-boi.png'

# various default values
URL_APPLICATION = 'https://soco.jm.u-psud.fr'
URL_DEFAULT='https://soco.jm.u-psud.fr'
INSTITUTION_PPALE="Université Paris Sud - Faculté Jean Monnet"
SALLE_PPALE="Salle G.Vedel, Faculté Jean Monnet"
EMAIL_ORGA="Secrétariat du Département de la Recherche <colloques.jean-monnet@u-psud.fr>"
EMAIL_SITE="Odile Bénassy <informatique-recherche.droit-eco-gestion@u-psud.fr>"
SIGNATURE_EMAILS="Service de la recherche\nFaculté Jean Monnet\nUniversité Paris Sud"
NOM_INTERFACE_ADMIN="Administration de SoCo"

# Optional features
AVEC_ETIQUETTES=False
AVEC_QRCODE=True
AVEC_RECURRENCE=False

# Flask_login
COOKIE_DURATION_DAYS = 30
LOGIN_MESSAGE = u'Merci de vous identifier'

# Logging
LOG_FILE = './logs/soco.log'

# Where to generate PDFs
FABDIR = basedir + '/soco/tex/'
TMPDIR = '/tmp/'
