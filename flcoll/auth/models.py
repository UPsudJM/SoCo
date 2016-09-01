from sqlalchemy import Column, Integer, String
from ldap3 import Server, Connection
from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired
from flcoll import app, Base


def get_ldap_connection():
    conn = ldap.Connection(app.config['LDAP_PROVIDER_URL'], auto_bind=True)
    return conn


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(100))

    def __init__(self, username, password):
        self.username = username

    @staticmethod
    def try_login(username, password):
        server = Server(app.config['LDAP_PROVIDER_URL']) #, use_ssl=True)
        conn = Connection(server, 'uid=%s,ou=people,dc=ldap,dc=u-psud,dc=fr'' % username', password)
        conn.bind()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class LoginForm(Form):
    username = TextField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])
