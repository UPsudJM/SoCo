"""
§ This file is part of SoCo.                                            §
§                                                                       §
§ SoCo is free software: you can redistribute it and/or modify          §
§ it under the terms of the GNU General Public License as published by  §
§ the Free Software Foundation, either version 3 of the License, or     §
§ (at your option) any later version.                                   §
§                                                                       §
§ SoCo is distributed in the hope that it will be useful,               §
§ but WITHOUT ANY WARRANTY; without even the implied warranty of        §
§ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         §
§ GNU General Public License for more details.                          §
§                                                                       §
§ You should have received a copy of the GNU General Public License     §
§ along with SoCo.  If not, see <http://www.gnu.org/licenses/>.         §
§                                                                       §
§ © 2016-2017 Odile Bénassy, Université Paris Sud                       §
§                                                                       §
"""
# coding: utf-8

from flask import Flask
from flask_babelex import Babel
from flask_restful import Api
from datetime import timedelta
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, LOG_FILE
from config import COOKIE_DURATION_DAYS, LOGIN_MESSAGE, SECRET_KEY, LOGO_DEFAULT, URL_DEFAULT

app = Flask(__name__)
app.config.from_object('config')
babel = Babel(app)
api = Api(app)
app.secret_key = SECRET_KEY

from jinja2 import Environment
jinja_env = Environment(extensions=['jinja2.ext.i18n'])
#translations = jinja_env.get_gettext_translations()
#jinja_env.install_gettext_translations(translations)

from flask_login import LoginManager
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'auth.login'
lm.cookie_duration = timedelta(COOKIE_DURATION_DAYS)
lm.login_message = LOGIN_MESSAGE

from flask_mail import Mail
mail = Mail(app)

if app.config['AVEC_QRCODE']:
    from flask_qrcode import QRcode
    qrcode = QRcode(app)

# Database access
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import DB_ENGINE
if DB_ENGINE == 'postgresql':
    from config import PGSQL_DATABASE_USER, PGSQL_DATABASE_PASSWORD, PGSQL_DATABASE_DB, PGSQL_DATABASE_HOST
    SQLALCHEMY_DATABASE_URI = 'postgresql://' + PGSQL_DATABASE_USER + ":" + PGSQL_DATABASE_PASSWORD + "@" + PGSQL_DATABASE_HOST + "/" + PGSQL_DATABASE_DB
elif DB_ENGINE == 'mysql':
    from config import MYSQL_DATABASE_USER, MYSQL_DATABASE_PASSWORD, MYSQL_DATABASE_DB, MYSQL_DATABASE_HOST
    SQLALCHEMY_DATABASE_URI = 'mysql://' + MYSQL_DATABASE_USER + ":" + MYSQL_DATABASE_PASSWORD + "@" + MYSQL_DATABASE_HOST + "/" + MYSQL_DATABASE_DB
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import soco.models
    import soco.auth.models
    Base.metadata.create_all(bind=engine)

def test_data():
    from sqlalchemy.exc import IntegrityError
    from soco.auth.models import User
    adminuser = User('admin', gecos='Admin User')
    adminuser.set_password(User.hash_pwd('admin'))
    adminuser.set_role('admin')
    db_session.add(adminuser)
    testuser = User('demo', gecos='Test User')
    testuser.set_password(User.hash_pwd('demo'))
    db_session.add(testuser)
    try:
        db_session.commit()
    except IntegrityError as err:
        db_session.rollback()
        print("Erreur d'intégrité")
        if 'uc_usn' in str(err.orig):
            print("Ce nom d'utilisateur existe déjà dans la base")

"""
def clear_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import soco.models
    Base.metadata.drop_all(bind=engine)
"""

if 'db' in __file__:
    from soco import models
else:
    from soco import views, models
    from soco.auth.views import auth
    app.register_blueprint(auth)

if "test" not in __file__ and not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'soco failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(LOG_FILE, 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('SoCo startup')
