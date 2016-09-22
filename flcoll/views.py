# -*- Coding: utf-8 -*-

from datetime import datetime
#import time
#from config import LANGUAGES
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin.form.upload import ImageUploadField
from flcoll import app, babel, db_session, lm
from .models import Evenement, Formulaire, Personne, Inscription
from .forms import InscriptionForm
from wtforms.validators import DataRequired


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

@app.route('/colloque/<int:flform>', methods=['GET', 'POST'])
def flcoll(flform):
    formulaire = Formulaire.query.filter_by(id=flform).first()
    if formulaire == None:
        flash('Formulaire %d non trouvé' % flform)
        return internal_error('Formulaire %d non trouvé' % flform)
    form = InscriptionForm(formulaire)
    if form.validate_on_submit():
        personne = Personne(nom=form.nom.data, prenom=form.prenom.data,
                                email=form.email.data, telephone=form.telephone.data,
                                organisation=form.organisation.data, fonction=form.fonction.data)
        #inscription = Inscription(form.nom.data, form.prenom.data, form.email.data, form.telephone.data)
        inscription = Inscription(formulaire.evenement, personne)
        db_session.add(inscription)
        db_session.commit()
        flash('Votre inscription a bien été effectuée.')
    return render_template('flform.html', form=form, formulaire=formulaire, evenement=formulaire.evenement, current_user=current_user)

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


class FlcollModelView(ModelView):
    form_excluded_columns = ['upd']

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))


class EvenementView(FlcollModelView):
    page_size = 20  # the number of entries to display on the list view
    action_disallowed_list = ['delete']
    can_export = True
    can_view_details = True
    column_labels = dict(sstitre= 'Sous-titre', date_debut='Date', uid_organisateur='Organisateur/trice',
                             resume='Résumé', gratuite='Gratuit', upd='Mis à jour le')
    column_choices = {'gratuite': [ (True, 'oui'), (False, 'non') ] }
    column_exclude_list = ['upd', 'resume' ]
    column_sortable_list = ['titre', 'date_debut', 'uid_organisateur']
    column_filters = ['titre', 'lieu', 'uid_organisateur', 'gratuite']
    column_default_sort = 'date_debut'
    column_descriptions = dict(
        titre='Titre de l\'événement',
        sstitre='Sous-titre de l\'événement',
        lieu='Lieu de l\'événement <em>(vous pouvez laisser vide s\'il s\'agit de la salle Vedel)</em>',
        uid_organisateur='L\'identifiant Paris Sud <code>prenom.nom</code> de l\'organisateur/trice',
        gratuite = 'L\'entrée est-elle libre ?'
        )
    column_formatters = dict(date_debut=lambda v, c, m, p: m.date_debut.date(),
                                 date_fin=lambda v, c, m, p: (m.date_fin and m.date_fin!=m.date_debut and m.date_fin.date()) or "",
                                 )
    form_args = {
        'titre': {'label': 'Titre', 'validators': [DataRequired()]},
        'sstitre': {'label': 'Sous-titre'},
        'date_debut': {'label': 'Date', 'validators': [DataRequired()]},
        'date_fin': {'label': 'Date de fin (si nécessaire)'},
        'resume' : {'label': 'Résumé'},
        'gratuite' : {'label': 'Gratuité'}
        }
    form_excluded_columns = ['upd']
    form_overrides = dict(logo=ImageUploadField)
    inline_models = [(Formulaire, dict(form_columns=['id', 'date_ouverture_inscriptions', 'date_cloture_inscriptions']))]


class FormulaireView(FlcollModelView):
    column_exclude_list = ['upd', 'texte_restauration_1' , 'texte_restauration_2']
    form_excluded_columns = ['upd']
    form_ajax_refs = {
        'evenement': QueryAjaxModelLoader('evenement', db_session, Evenement, fields=['titre'], page_size=10)
        }
    #ajax_update = ['date_ouverture_inscriptions']


class PersonneView(FlcollModelView):
    can_export = True
    form_args = {
        'prenom' : {'label': 'Prénom'},
        'telephone' : {'label': 'Téléphone'}
    }
    inline_models = [(Inscription, dict(form_columns=['id', 'evenement', 'attestation_demandee']))]


class InscriptionView(FlcollModelView):
    can_export = True
    form_excluded_columns = ['date_inscription']
    form_ajax_refs = {
        'evenement': QueryAjaxModelLoader('evenement', db_session, Evenement, fields=['titre'], page_size=10),
        'personne': QueryAjaxModelLoader('personne', db_session, Personne, fields=['nom', 'prenom'], page_size=10)
        }


admin = Admin(app, name='Colloques Jean Monnet', template_mode='bootstrap3')
admin.add_view(EvenementView(Evenement, db_session))
admin.add_view(FormulaireView(Formulaire, db_session))
admin.add_view(PersonneView(Personne, db_session))
admin.add_view(InscriptionView(Inscription, db_session))
