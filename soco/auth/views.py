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

from flask import request, render_template, flash, redirect, url_for, Blueprint, g, session
from flask_login import current_user, login_user, logout_user, login_required
from flask_babelex import gettext, lazy_gettext
from soco import app, lm, db_session
from soco.auth.models import User, LoginForm, UserForm

auth = Blueprint('auth', __name__)


@lm.user_loader
def load_user(user_id):
    if user_id:
        user = User.query.get(int(user_id))
        if user:
            user.authenticate()
            g.gecos = user.get_gecos()
            #print('gecos=', g.gecos)
            return user
    g.gecos = None
    return None

@auth.before_request
def get_current_user():
    g.user = current_user

@auth.route('/')
@auth.route('/home')
def home():
    return render_template('home.html')

@auth.route('/login', methods=['POST', 'GET'])
def login():
    if current_user is not None \
        and current_user.is_authenticated:
        flash('Vous êtes déjà identifié-e.')
        return redirect(url_for('suivi_index'))

    form = LoginForm(request.form) #, nexturl=request.args['next'])
    if request.args and request.args.get('next'):
        form.nexturl.data = request.args['next']

    if request.method == 'POST' and form.validate():
        username = request.form.get('username')
        password = request.form.get('password')
        rememberme = request.form.get('rememberme')
        user = User.get_user(username)

        auth_ok, auth_db_ok, auth_ldap_ok = False, False, False
        if user:
            try:
                auth_db_ok = User.try_db_login(username, password)
            except:
                raise
        auth_ok = auth_db_ok
        if not auth_ok and app.config['USE_LDAP']:
            try:
                auth_ldap_ok = User.try_ldap_login(username, password)
            except:
                raise
            finally:
                auth_ok = auth_ldap_ok
        if not auth_ok:
            flash('Login ou mot de passe invalide. Veuillez ré-essayer', 'danger')
            return render_template('login.html', form=form)

        if type(auth_ok) == type((1,)) and len(auth_ok) > 1:
            session.update(gecos = auth_ok[1])
            user_email = auth_ok[2]
        else:
            user_email = None

        if not user and auth_ldap_ok:
           user = User(username, password='ldap', email=user_email)
           db_session.add(user)
           db_session.commit()
        user.authenticate()
        login_user(user, remember = rememberme)
        flash(gettext('Identification réussie.'), 'auth success')
        nexturl = request.form.get('nexturl')
        # next_is_valid should check if the user has valid
        # permission to access the `next` url
        # FIXME
        #if not next_is_valid(nexturl):
        #    return flask.abort(400)
        return redirect(nexturl or url_for('suivi_index'))
    if form.errors:
        flash(form.errors, 'danger')

    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    if not session.get('rememberme'):
        session.clear()
    if session.get('gecos'):
        session.pop('gecos')
    logout_user()
    return redirect(url_for('index'))


@app.route('/createuser', methods=['GET', 'POST'])
def createuser():
    form = UserForm()
    if form.validate_on_submit():
        deja = User.get_user(form.username.data)
        if deja:
            flash(gettext('Cet utilisateur existe déjà'))
            return render_template('createuser.html', form=form)
        hashed = User.hash_pwd(form.password.data)
        newuser = User(username=form.username.data, password=hashed, gecos=form.gecos.data)
        db_session.add(newuser)
        db_session.commit()
        flash(gettext('L\'utilisateur \'{username}\' a bien été créé').format(username=form.username.data))
        return redirect(url_for('index'))
    return render_template('createuser.html', form=form)
