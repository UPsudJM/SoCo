# -*- Coding: utf-8 -*-

from datetime import datetime
#from config import LANGUAGES
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flcoll import app, babel, db_session, lm
from .models import Evenement
from .forms import EvenementForm

@babel.localeselector
def get_locale():
    return "fr"
    #return request.accept_languages.best_match(LANGUAGES.keys())

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db_session.rollback()
    return render_template('500.html'), 500
            
@app.route('/')
@app.route('/index')
#@login_required
def index():
#        return "Hello, World!"
    #user = {'nickname': 'Miguel'}  # fake user
    evenements = Evenement.query.all()
    return render_template('index.html', title='Conferences', evenements=evenements)

"""
@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        if (form.openid.data=="odile"):
            redirect(url_for('index'))

        #flash('Login requested for OpenID="%s", remember_me=%s' %
        #          (form.openid.data, str(form.remember_me.data)))
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)
"""

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/colloque/<evt>')
#@login_required
def colloque(evt):
    evenement = Evenement.query.filter_by(id=evt).first()
    if evenement == None:
        flash('Évenement %s non trouvé' % evt)
        return internal_error('Évenement %s non trouvé')
    return render_template('colloque.html', evenement=evenement)

@app.route('/edit', methods=['GET', 'POST'])
#@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db_session.add(g.user)
        db_session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('index'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
        return render_template('edit.html', form=form)

admin = Admin(app, name='Colloques Jean Monnet', template_mode='bootstrap3')
admin.add_view(ModelView(Evenement, db_session))
