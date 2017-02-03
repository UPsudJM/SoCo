from flask import Flask
from flask_babelex import Babel
from flask_login import LoginManager
from flask_restful import Api
from datetime import timedelta
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, LOG_FILE
from config import COOKIE_DURATION_DAYS, LOGIN_MESSAGE

app = Flask(__name__)
app.config.from_object('config')
babel = Babel(app)
api = Api(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'auth.login'
lm.cookie_duration = timedelta(COOKIE_DURATION_DAYS)
lm.login_message = LOGIN_MESSAGE

from flask_mail import Mail
mail = Mail(app)

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import PGSQL_DATABASE_USER, PGSQL_DATABASE_PASSWORD, PGSQL_DATABASE_DB, PGSQL_DATABASE_HOST

SQLALCHEMY_DATABASE_URI = 'postgresql://' + PGSQL_DATABASE_USER + ":" + PGSQL_DATABASE_PASSWORD + "@" + PGSQL_DATABASE_HOST + "/" + PGSQL_DATABASE_DB
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

"""
def clear_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import soco.models
    Base.metadata.drop_all(bind=engine)
"""

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
    app.logger.info('soco startup')