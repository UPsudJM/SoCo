from sqlalchemy import Column, Integer, String
from ldap3 import Server, Connection
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, HiddenField, BooleanField
from wtforms.validators import InputRequired
from flcoll import app, Base
from config import COOKIE_DURATION_DAYS


class User(Base):
    __tablename__ = 'utilisateur'
    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    role = Column(String(10))
    is_authenticated = False
    is_active = True
    is_anonymous = False
    is_admin = False
    is_superadmin = False

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
                try:
                    self.get_gecos()
                except:
                    pass
                return True
        except:
            print('error in bind', conn.result, repr(conn))
            return False

    def authenticate(self):
        self.is_authenticated = True
        if 'admin' in self.role:
            self.is_admin = True
        if 'super' in self.role:
            self.is_superadmin = True

    def deactive(self):
        self.is_active = False

    def get_id(self):
        return str(self.id)

    def get_gecos(self, connection):
        search_filter = "(mail=%s*)" % self.username
        print(search_filter)
        connection.search(search_filter)
        print(connection.entries)
        self.gecos = gecos

class LoginForm(FlaskForm):
    username = TextField('Nom d\'utilisateur', [InputRequired()])
    password = PasswordField('Mot de passe', [InputRequired()])
    nexturl = HiddenField()
    rememberme = BooleanField('Se souvenir de moi <small>(pendant %d jours)</small>' % COOKIE_DURATION_DAYS)
