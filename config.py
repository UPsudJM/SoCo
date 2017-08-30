# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'psql', 'migrate_repo')

WTF_CSRF_ENABLED = True
SECRET_KEY = 'bibliotheque pierre pactet'
SQLALCHEMY_TRACK_MODIFICATIONS = True

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DOMAIN = 'u-psud.fr'

# administrator list
ADMINS = ['odile.benassy@u-psud.fr']

#LDAP_PROVIDER_URL = 'ldap://ldaps.u-psud.fr:636'
LDAP_PROVIDER_URL = 'ldaps.u-psud.fr'
#LDAP_PROTOCOL_VERSION = 3
LDAP_SEARCH_BASE = 'dc=u-psud, dc=fr'

# Database
PGSQL_DATABASE_DB = 'soco'
PGSQL_DATABASE_HOST = 'localhost'
from secret import PGSQL_DATABASE_USER, PGSQL_DATABASE_PASSWORD

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
LOGO_DEFAULT='Logo-JEAN-MONNET_UPSaclay-BLEU-carre.png'
URL_DEFAULT='http://www.jm.u-psud.fr'
INSTITUTION_DEFAULT="Université Paris Saclay - Faculté Jean Monnet"

# Flask_login
COOKIE_DURATION_DAYS = 30
LOGIN_MESSAGE = u'Merci de vous identifier'

# Logging
LOG_FILE = '/var/log/soco.log'

# Where to generate PDFs
FABDIR = basedir + '/soco/tex/'
TMPDIR = '/tmp/'
