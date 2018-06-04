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
§ © 2016-2018 Odile Bénassy, Université Paris Sud                       §
§                                                                       §
"""
# coding: utf-8

import enum
from sqlalchemy import Column, Integer, String, Enum, UniqueConstraint
from flask_babelex import gettext
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, HiddenField, BooleanField, RadioField
from wtforms.validators import InputRequired
from soco import app, Base
if app.config['USE_LDAP']:
    from ldap3 import Server, Connection
if app.config['USE_PWHASH']:
    from passlib.hash import pbkdf2_sha256


class RoleEnum(enum.Enum):
    visitor = "visitor"
    user = "user"
    admin = "admin"
    superadmin = "superadmin"


class User(Base):
    __tablename__ = 'utilisateur'
    __table_args__ = (UniqueConstraint('username', name='uc_usn'), UniqueConstraint('email', name='uc_email'),)
    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    password = Column(String(200))
    role = Column('role', Enum(RoleEnum))
    gecos = Column(String(100))
    email = Column(String(200))
    is_authenticated = False
    is_active = True
    is_anonymous = False
    is_admin = False
    is_superadmin = False

    def __init__(self, username, password=None, gecos=None, email=None):
        self.username = username
        self.password = password
        self.role = 'user'
        self.gecos = gecos
        self.email = email
        self.is_authenticated = False

    def __str__(self):
        return self.gecos or self.username

    @staticmethod
    def hash_pwd(p):
        return pbkdf2_sha256.hash(p)

    def set_password(self, s):
        self.password = s

    def set_role(self, role):
        self.role = role

    def get_id(self):
        return str(self.id)

    def get_username(self):
        return self.username

    def get_gecos(self):
        if self.gecos:
            return self.gecos
        return self.username

    def is_ldap_user(self):
                return self.password == 'ldap'

    @classmethod
    def get_user(self, username):
        user = self.query.filter_by(username=username).first()
        return user

    @classmethod
    def get_user_by_email(self, email):
        user = self.query.filter_by(email=email).first()
        return user

    @classmethod
    def try_db_login(self, username, password):
        user = self.get_user(username)
        if user:
            if app.config['USE_PWHASH']:
                auth_ok = pbkdf2_sha256.verify(password, user.password)
            else:
                auth_ok =  (password == user.password)
            if auth_ok:
                return (True, user.gecos, user.email,)
        return False

    @staticmethod
    def try_ldap_login(username, password, with_gecos=True, with_email=True):
        server = Server(app.config['LDAP_PROVIDER_URL'], use_ssl=True)
        conn = Connection(server, app.config['LDAP_USER_PATT'] % username, password)
        try:
            conn.bind()
        except:
            print('error in bind', conn.result, repr(conn))
            return False
        if conn.result['result']:
            return False
        if with_gecos or with_email:
            try:
                gecos, email = User.get_gecos_and_email(username, conn)
                return (True, gecos, email,)
            except:
                print('error retrieving gecos and email')
                return (True, None, None)
        return True

    def authenticate(self):
        self.is_authenticated = True
        if 'admin' in self.role.name:
            self.is_admin = True
        if 'super' in self.role.name:
            self.is_superadmin = True

    def deactive(self):
        self.is_active = False

    @staticmethod
    def get_gecos_and_email(username, connection):
        search_base = app.config['LDAP_SEARCH_BASE']
        search_filter = "(mail=%s*)" % username
        print(search_filter)
        connection.search(search_base = app.config['LDAP_SEARCH_BASE'],
                              search_filter = "(mail=%s*)" % username,
                              attributes = ['cn', 'givenName', 'gecos', 'mail'],)
        try:
            gecos = connection.entries[0].gecos.value
        except:
            print('Cannot find gecos value')
        try:
            email = connection.entries[0].email.value
        except:
            print('Cannot find email value')
        return gecos, email


class LoginForm(FlaskForm):
    username = TextField(gettext('Nom d\'utilisateur'), validators = [InputRequired()])
    password = PasswordField(gettext('Mot de passe'), validators = [InputRequired()])
    nexturl = HiddenField()
    rememberme = BooleanField(gettext('Se souvenir de moi <small>(pendant {duration} jours)</small>').format(duration = app.config['COOKIE_DURATION_DAYS']))


class UserForm(FlaskForm):
    username = TextField(gettext('Nom d\'utilisateur'), validators = [InputRequired()])
    password = TextField(gettext('Mot de passe'), validators = [InputRequired()])
    email = TextField(gettext('Adresse électronique'), validators = [InputRequired()])
    #role = RadioField(gettext('Rôle'), default = 'user', choices = [(e, e.name) for e in RoleEnum])
    gecos = TextField(gettext('Nom complet'))
