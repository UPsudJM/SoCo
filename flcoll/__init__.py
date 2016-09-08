import os
from flask import Flask
from flask_babelex import Babel
#from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

app = Flask(__name__)
babel = Babel(app)
app.config.from_object('config')
#db = SQLAlchemy(app)
#from flcoll.database import db_session

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import MYSQL_DATABASE_USER, MYSQL_DATABASE_PASSWORD, MYSQL_DATABASE_DB, MYSQL_DATABASE_HOST
from config import PGSQL_DATABASE_USER, PGSQL_DATABASE_PASSWORD, PGSQL_DATABASE_DB, PGSQL_DATABASE_HOST

#SQLALCHEMY_DATABASE_URI = 'mysql+oursql://' + MYSQL_DATABASE_USER + ":" + MYSQL_DATABASE_PASSWORD + "@" + MYSQL_DATABASE_HOST + "/" + MYSQL_DATABASE_DB
SQLALCHEMY_DATABASE_URI = 'postgresql://' + PGSQL_DATABASE_USER + ":" + PGSQL_DATABASE_PASSWORD + "@" + PGSQL_DATABASE_HOST + "/" + PGSQL_DATABASE_DB
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import flcoll.models
    Base.metadata.create_all(bind=engine)

from flcoll import views, models
from flcoll.auth.views import auth
app.register_blueprint(auth)

if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
    
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('microblog startup')
