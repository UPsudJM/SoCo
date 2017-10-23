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

from sqlalchemy import Column, Integer, String
from ldap3 import Server, Connection
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, HiddenField, BooleanField
from wtforms.validators import InputRequired
from soco import app, Base


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
        self.role = 'user'
        self.is_authenticated = False

    @staticmethod
    def try_login(username, password, with_gecos=True):
        server = Server(app.config['LDAP_PROVIDER_URL'], use_ssl=True)
        conn = Connection(server, 'uid=%s,ou=people,dc=u-psud,dc=fr' % username, password)
        try:
            conn.bind()
        except:
            print('error in bind', conn.result, repr(conn))
            return False
        if conn.result['result']:
            return False
        #self.username = username
        if with_gecos:
            try:
                gecos = User.get_gecos(username, conn)
                return (True, gecos,)
            except:
                pass
        else:
            pass
        return True

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

    @staticmethod
    def get_gecos(username, connection):
        search_base = app.config['LDAP_SEARCH_BASE']
        search_filter = "(mail=%s*)" % username
        print(search_filter)
        connection.search(search_base = app.config['LDAP_SEARCH_BASE'],
                              search_filter = "(mail=%s*)" % username,
                              attributes = ['cn', 'givenName', 'gecos'],)
        print(connection.entries)
        print(connection.entries[0])
        print(connection.entries[0].gecos.value)
        gecos = connection.entries[0].gecos.value
        return gecos

class LoginForm(FlaskForm):
    username = TextField('Nom d\'utilisateur', [InputRequired()])
    password = PasswordField('Mot de passe', [InputRequired()])
    nexturl = HiddenField()
    rememberme = BooleanField('Se souvenir de moi <small>(pendant %d jours)</small>' % app.config['COOKIE_DURATION_DAYS'])
