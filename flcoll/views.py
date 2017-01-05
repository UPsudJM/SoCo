# -*- Coding: utf-8 -*-

import datetime
from sqlalchemy.exc import IntegrityError
#from config import LANGUAGES
from config import LOGO_FOLDER, LOGO_EXTENSIONS, LOGO_URL_REL, LOGO_DEFAULT
from flask import render_template, flash, redirect, make_response, session, url_for, request, g, send_file
from flask_login import login_user, logout_user, current_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin.form.upload import ImageUploadField
from flcoll import app, babel, db_session, lm
from wtforms.validators import DataRequired
from .models import Organisation, Personne, Evenement, Formulaire, Inscription
from .forms import InscriptionForm, NcollForm
from .filters import datefr_filter, afflogo_filter
from .emails import confirmer_inscription
from .texenv import texenv, genere_pdf


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
    evenement = formulaire.evenement
    logo = evenement.logo
    if not logo:
        organisation = evenement.entite_organisatrice
        logo = organisation.logo
        if not logo:
            logo = LOGO_DEFAULT
    logofilename = afflogo_filter(logo)
    if formulaire == None:
        flash('Formulaire %d non trouvé' % flform)
        return internal_error('Formulaire %d non trouvé' % flform)
    if formulaire.date_ouverture_inscriptions > datetime.date.today():
        return render_template('erreur.html', msg='Les inscriptions pour cet événement ne sont pas encore ouvertes !')
    elif formulaire.date_cloture_inscriptions < datetime.date.today():
        return render_template('erreur.html', msg='Les inscriptions pour cet événement sont closes !')
    form = InscriptionForm(formulaire)
    if form.validate_on_submit():
        personne = Personne.query.filter_by(nom=form.nom.data, prenom=form.prenom.data,
                                                    email=form.email.data).first()
        #personne = Personne.query.filter_by(nom=form.nom.data, prenom=form.prenom.data,
        #                                        organisation=form.organisation.data).first()
        if personne == None:
            personne = Personne(nom=form.nom.data, prenom=form.prenom.data,
                                email=form.email.data)
        inscription = Inscription(evenement=formulaire.evenement, personne=personne)
        if form.telephone.data: inscription.telephone = form.telephone.data
        if form.fonction.data: inscription.fonction = form.fonction.data
        if form.organisation.data: inscription.organisation = form.organisation.data
        inscription.date_inscription = datetime.datetime.now()
        db_session.add(inscription)
        try:
            db_session.commit()
        except IntegrityError as err:
            db_session.rollback()
            if "uc_1" in str(err.orig):
                flash("Vous vous êtes déjà inscrit-e avec ces mêmes nom, prénom et organisation !")
            if "uc_2" in str(err.orig):
                flash("Vous vous êtes déjà inscrit-e avec ces mêmes nom, prénom et adresse électronique !")
            if "uc_3" in str(err.orig):
                flash("Vous êtes déjà inscrit-e à cet événement !")
        else:
            confirmer_inscription(personne.email, formulaire.evenement)
            flash("Votre inscription a bien été effectuée.")
            return redirect('/')
    return render_template('flform.html', form=form, formulaire=formulaire,
                               evenement=evenement,
                               logofilename=logofilename,
                               current_user=current_user)


@app.route('/new/')
@login_required
def new():
    form = NcollForm()
    return render_template('new.html', form=form, current_user=current_user)

@app.route('/suivi/')
@login_required
def suivi_index():
    evenements = Evenement.query.join("formulaire").join("inscription").filter(Evenement.date > datetime.datetime.now() - datetime.timedelta(days=15))
    nb_inscrits = {}
    for e in evenements:
        nb_inscrits[e.id] = len(e.inscription)
    return render_template("suivi_index.html", evenements=evenements, today=datetime.date.today(), nb_inscrits=nb_inscrits)

@app.route('/suivi/<int:evt>', methods=['GET', 'POST'])
@app.route('/suivi/<int:evt>/<action>', methods=['GET', 'POST'])
@login_required
def suivi(evt, action=None):
    evenement = Evenement.query.get(evt)
    inscrits = Inscription.query.filter_by(id_evenement=evt).all()
    formulaires = Formulaire.query.filter_by(id_evenement=evt).all()
    repas_1_existant = False
    texte_repas_1 = None
    for f in formulaires:
        if f.champ_restauration_1 == True:
            repas_1_existant = True
            texte_repas_1 = f.texte_restauration_1
            break
    repas_2_existant = False
    texte_repas_2 = None
    for f in formulaires:
        if f.champ_restauration_2 == True:
            repas_2_existant = True
            texte_repas_2 = f.texte_restauration_2
            break
    if evenement == None:
        flash('Événement %d non trouvé' % evt)
        return internal_error('Evenement %d non trouvé' % evt)
    if action == "csv":
        csv = render_template(
            'inscrits.csv',
            evenement=evenement, inscrits=inscrits, repas_1_existant=repas_1_existant,
            texte_repas_1=texte_repas_1, repas_2_existant=repas_2_existant, texte_repas_2=texte_repas_2)
        csv_latin1 = csv.encode("latin-1")
        response = make_response(csv_latin1)
        response.headers["Content-Type"] = "application/csv; charset=iso-8859-15"
        response.headers["Content-Disposition"] = "attachment; filename=inscrits-colloque-%d-%s.csv" % (
            evt, datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M"))
        return response
    if action == "mails":
        return render_template('mails_inscrits.txt', inscrits = inscrits)
    if action == "listepdf":
        texcode = texenv.get_template('liste_presents.tex').render(evenement=evenement, inscrits=inscrits)
        try:
            resultat = genere_pdf(texcode)
        except:
            flash("Erreur dans la génération du document. Le plus souvent, c'est une erreur d'encodage due à un caractère inhabituel dans un nom propre")
            return internal_error('Impossible de générer le PDF listepdf pour %d' % evt)
        if type(resultat) != type(""):
            flash(str(resultat))
            return render_template('500.html')
        return send_file(resultat, as_attachment=True, attachment_filename="presents-colloque-%d-%s.pdf" % (
            evt, datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M")))
    if action == "emargement":
        texcode = texenv.get_template('liste_emargement.tex').render(evenement=evenement, inscrits=inscrits)
        resultat = genere_pdf(texcode)
        if type(resultat) != type(""):
            flash(str(resultat))
            return render_template('500.html')
        return send_file(resultat, as_attachment=True, attachment_filename="emargement-colloque-%d-%s.pdf" % (
            evt, datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M")))
    if action == "badges":
        texcode = render_template('badges.tex', inscrits=inscrits)
        response = make_response(genere_badges(texcode))
        response.headers["Content-Disposition"] = "attachment; filename=badges-colloque-%d-%s.pdf" % (
            evt, datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M"))
        return response
    return render_template(
        'suivi.html',
        evenement=evenement, inscrits=inscrits, repas_1_existant=repas_1_existant,
        texte_repas_1=texte_repas_1, repas_2_existant=repas_2_existant, texte_repas_2=texte_repas_2)


class FlcollModelView(ModelView):
    form_excluded_columns = ['upd']

    def is_accessible(self):
        try:
            return current_user.is_authenticated
        except:
            return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))


class LogoField(ImageUploadField):
    def __init__(self, label=None, validators=None,
                     base_path=None, relative_path=None,
                     namegen=None, allowed_extensions=None,
                     max_size=None,
                     thumbgen=None, thumbnail_size=None,
                     permission=0o666,
                     url_relative_path=None, endpoint='static',
                     **kwargs):
        ImageUploadField.__init__(self, label, validators, LOGO_FOLDER, relative_path, namegen, LOGO_EXTENSIONS,
                             max_size, thumbgen, thumbnail_size, permission, LOGO_URL_REL, endpoint, **kwargs)


class EvenementView(FlcollModelView):
    page_size = 20  # the number of entries to display on the list view
    action_disallowed_list = ['delete']
    can_export = True
    can_view_details = True
    column_labels = dict(sstitre= 'Sous-titre', date='Date', uid_organisateur='Organisateur/trice',
                             resume='Résumé', gratuite='Gratuit', entite_organisatrice='Entité organisatrice',
                             upd='Mis à jour le')
    column_choices = {'gratuite': [ (True, 'oui'), (False, 'non') ] }
    column_exclude_list = ['upd', 'resume' ]
    column_sortable_list = ['titre', 'date', 'uid_organisateur']
    column_filters = ['titre', 'lieu', 'uid_organisateur', 'gratuite']
    column_default_sort = 'date'
    column_descriptions = dict(
        titre='Titre de l\'événement',
        sstitre='Sous-titre de l\'événement',
        lieu='Lieu de l\'événement <em>(vous pouvez laisser vide s\'il s\'agit de la salle Vedel)</em>',
        uid_organisateur='L\'identifiant Paris Sud <code>prenom.nom</code> de l\'organisateur/trice',
        gratuite = 'L\'entrée est-elle libre ?'
        )
    #column_formatters = dict(date=lambda v, c, m, p: m.date.date(),
    #                             date_fin=lambda v, c, m, p: (m.date_fin and m.date_fin!=m.date and m.date_fin.date()) or "",
    #                             )
    form_args = {
        'titre': {'label': 'Titre', 'validators': [DataRequired()]},
        'sstitre': {'label': 'Sous-titre'},
        'date': {'label': 'Date', 'validators': [DataRequired()]},
        'date_fin': {'label': 'Date de fin (si nécessaire)'},
        'logo' : {'label': 'Logo (s\'il est différent de celui de l\'entité organisatrice)'},
        'resume' : {'label': 'Résumé'},
        'gratuite' : {'label': 'Gratuité'},
        'inscription' : {'label': 'Personnes inscrites'}
        }
    form_excluded_columns = ['upd']
    form_overrides = dict(logo=ImageUploadField)
    inline_models = [(Formulaire, dict(form_columns=['id', 'date_ouverture_inscriptions', 'date_cloture_inscriptions']))]


class FormulaireView(FlcollModelView):
    column_exclude_list = ['upd', 'texte_restauration_1' , 'texte_restauration_2']
    column_descriptions = dict(
        organisateur_en_copie = "Souhaitez-vous que l'organisateur/trice reçoive un mail à chaque inscription ?",
        champ_attestation = "Les personnes qui s'inscrivent peuvent demander une attestation de présence",
        champ_restauration_1 = "Pour pouvoir s'inscrire à un repas",
        texte_restauration_1 = "Le texte de la question correspondante",
        champ_restauration_2 = "2ème possibilité pour pouvoir s'inscrire à un repas",
        texte_restauration_2 = "Le texte de la question correspondante"
        )
    form_excluded_columns = ['upd']
    form_ajax_refs = {
        'evenement': QueryAjaxModelLoader('evenement', db_session, Evenement, fields=['titre'], page_size=10)
        }
    #ajax_update = ['date_ouverture_inscriptions']


class OrganisationView(FlcollModelView):
    can_export = True
    form_args = {
        'nom': {'label' : 'Nom de l\'organisation'},
        'interne' : {'label': 'Est-ce une organisation interne, susceptible d\'organiser des événements ?'},
        'email': {'label' : 'Adresse mail de contact'},
        'evenement' : {'label' : 'Événements'}
        }
    form_overrides = dict(logo=LogoField)
    #inline_models = [(Evenement, dict(form_columns=['id', 'titre', 'date']))]
    form_ajax_refs = {
        'evenement': QueryAjaxModelLoader('evenement', db_session, Evenement, fields=['titre'], page_size=10),
        'personne': QueryAjaxModelLoader('personne', db_session, Personne, fields=['nom', 'prenom'], page_size=10)
        }


class PersonneView(FlcollModelView):
    can_export = True
    form_args = {
        'prenom' : {'label': 'Prénom'}
    }
    inline_models = [(Inscription, dict(form_columns=['id', 'evenement', 'attestation_demandee']))]
    form_ajax_refs = {
        'organisation': QueryAjaxModelLoader('organisation', db_session, Organisation, fields=['nom'], page_size=10)
        }


class InscriptionView(FlcollModelView):
    can_export = True
    form_args = {
        'telephone' : {'label': 'Téléphone'}
    }
    form_excluded_columns = ['date_inscription']
    form_ajax_refs = {
        'evenement': QueryAjaxModelLoader('evenement', db_session, Evenement, fields=['titre'], page_size=10),
        'personne': QueryAjaxModelLoader('personne', db_session, Personne, fields=['nom', 'prenom'], page_size=10)
        }


admin = Admin(app, name='Colloques Jean Monnet', template_mode='bootstrap3')
admin.add_view(EvenementView(Evenement, db_session))
admin.add_view(FormulaireView(Formulaire, db_session))
admin.add_view(OrganisationView(Organisation, db_session))
admin.add_view(PersonneView(Personne, db_session))
admin.add_view(InscriptionView(Inscription, db_session))
