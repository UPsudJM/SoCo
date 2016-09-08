from sqlalchemy import Column, Integer, String
from ldap3 import Server, Connection
from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired
from flcoll import app, Base


class User(Base):
    __tablename__ = 'utilisateur'
    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    is_authenticated = False
    is_active = True
    is_anonymous = False

    def __init__(self, username):
        self.username = username
        self.is_authenticated = False

    @staticmethod
    def try_login(username, password):
        server = Server(app.config['LDAP_PROVIDER_URL'], use_ssl=True)
        conn = Connection(server, 'uid=%s,ou=people,dc=u-psud,dc=fr' % username, password)
        try:
            conn.bind()
            if conn.result['result']:
                return False
            else:
                return True
        except:
            print('error in bind', conn.result, repr(conn))
            return False

    def authenticate(self):
        self.is_authenticated = True

    def deactive(self):
        self.is_active = False

    def get_id(self):
        return str(self.id)


class LoginForm(Form):
    username = TextField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])
