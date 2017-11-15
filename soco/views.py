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

import datetime
from sqlalchemy.exc import IntegrityError
#from config import LANGUAGES
from flask import render_template, flash, redirect, make_response, session, url_for, request, g, send_file
from flask_login import login_user, logout_user, current_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin.form.upload import ImageUploadField
from flask_babelex import gettext, lazy_gettext
from soco import app, babel, db_session, lm
from wtforms.validators import DataRequired
from functools import wraps
from .models import Organisation, Lieu, Evenement, Formulaire, Personne, Inscription
from .forms import InscriptionForm, NcollForm
from .filters import datefr_filter, datetimefr_filter, afflogo_filter
from .emails import confirmer_inscription
from .texenv import texenv, genere_pdf, TPL_ETIQUETTE_VIDE, fabrique_page_etiquettes


@babel.localeselector
def get_locale():
    return "fr"
    #return request.accept_languages.best_match(LANGUAGES.keys())

def required_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                flash(gettext('Vous n\'avez pas les droits d\'accès à cette page'),'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper

@app.context_processor
def parametres_institution():
    return dict(nom_institution = app.config["INSTITUTION_PPALE"],
                lieu_par_default = app.config["SALLE_PPALE"],
                email_orga = app.config['EMAIL_ORGA'],
                email_site = app.config['EMAIL_SITE'],
                signature_emails = app.config['SIGNATURE_EMAILS'])

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db_session.rollback()
    return render_template('500.html'), 500

@app.route('/')
@app.route('/index')
# ECRIRE LES RESTRICTIONS DANS LA FONCTION
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

@app.route('/colloque/<int:flform>', methods=['GET', 'POST'])
@app.route('/event/<int:flform>', methods=['GET', 'POST'])
def soco(flform):
    formulaire = Formulaire.query.filter_by(id=flform).first()
    if not formulaire:
        return render_template('404.html')
    evenement = formulaire.evenement
    logo0, logo, url = evenement.infos_comm()
    logofilename0, logofilename = afflogo_filter(logo0), ""
    if logo:
        logofilename = afflogo_filter(logo)
    if formulaire.date_ouverture_inscriptions > datetime.date.today():
        return render_template('erreur.html', msg=gettext('Les inscriptions pour cet événement ne sont pas encore ouvertes !'))
    elif formulaire.date_cloture_inscriptions < datetime.date.today():
        return render_template('erreur.html', msg=gettext('Les inscriptions pour cet événement sont closes !'))
    form = InscriptionForm(formulaire)
    if form.validate_on_submit():
        personne = Personne.query.filter_by(nom=form.nom.data, prenom=form.prenom.data,
                                                    email=form.email.data).first()
        #personne = Personne.query.filter_by(nom=form.nom.data, prenom=form.prenom.data,
        #                                        organisation=form.organisation.data).first()
        if personne == None:
            personne = Personne(nom=form.nom.data, prenom=form.prenom.data,
                                email=form.email.data)
        inscription = Inscription(evenement=evenement, personne=personne)
        inscription.badge1 = form.badge1.data
        inscription.badge2 = form.badge2.data
        if form.telephone.data:
            inscription.telephone = form.telephone.data
        if form.fonction.data:
            inscription.fonction = form.fonction.data
        if form.organisation.data:
            inscription.organisation = form.organisation.data
        inscription.date_inscription = datetime.datetime.now()
        # Champs facultatifs
        if formulaire.champ_attestation and form.attestation_demandee.data:
            inscription.attestation_demandee = form.attestation_demandee.data
        if formulaire.champ_type_inscription and form.type_inscription.data:
            inscription.type_inscription = form.type_inscription.data
        if form.jours_de_presence.data: # booléens à attraper
            inscription.jours_de_presence = form.jours_de_presence.data
        if formulaire.champ_restauration_1 and form.inscription_repas_1.data:
            inscription.inscription_repas_1 = form.inscription_repas_1.data
        if formulaire.champ_restauration_2 and form.inscription_repas_2.data:
            inscription.inscription_repas_2 = form.inscription_repas_2.data
        if formulaire.champ_libre_1 and form.reponse_question_1.data:
            inscription.reponse_question_1 = form.reponse_question_1.data
        if formulaire.champ_libre_2 and form.reponse_question_2.data:
            inscription.reponse_question_2 = form.reponse_question_2.data
        db_session.add(inscription)
        try:
            db_session.commit()
        except IntegrityError as err:
            db_session.rollback()
            flash(lazy_gettext("Erreur d'intégrité"), 'erreur')
            if "uc_porg" in str(err.orig):
                flash(lazy_gettext("Vous vous êtes déjà inscrit-e avec ces mêmes nom, prénom et organisation !"), 'erreur')
            if "uc_pers" in str(err.orig):
                flash(lazy_gettext("Vous vous êtes déjà inscrit-e avec ces mêmes nom, prénom et adresse électronique !"), 'erreur')
            if "uc_insc" in str(err.orig):
                flash(lazy_gettext("Vous êtes déjà inscrit-e à cet événement !"), 'erreur')
        else:
            confirmer_inscription(personne.email, formulaire.evenement)
            flash(gettext("Votre inscription a bien été effectuée."))
            if app.config['AVEC_QRCODE']:
                qrstring = gettext("SoCo - Événement {evt} : {prenom} {nom} est inscrit-e sous le numéro {num}.").format(
                    evt = evenement.titre, prenom = personne.prenom, nom = personne.nom, num = inscription.id)
            else:
                qrstring = ''
            return render_template('end.html', evenement = evenement, qrstring=qrstring,
                                       logofilename = logofilename, lienevt = url)
    return render_template('flform.html', form=form, formulaire=formulaire, evenement=evenement, speaker=False,
                               logofilename0=logofilename0, logofilename=logofilename, url0 = url0, lienevt = url,
                               current_user=current_user)


@app.route('/end')
def end():
    id_evenement = session.id_evenement
    evenement = Evenement.query.filter_by(id=id_evenement).first()
    return render_template('end.html', evenement=evenement, logofilename=session.logofilename)

@app.route('/planning/<token>')
@app.route('/cal/<token>')
def planning(token):
    # on vérifie d'abord que la personne existe
    # et on envoie le planning de la personne
    personne = Personne.query.filter_by(token=token).first()
    if not personne:
        return render_template('404.html')
    inscriptions = Personne.inscription
    return render_template('planning.html', personne=personne, inscriptions=inscriptions)

@app.route('/speaker/<int:flform>', methods=['GET', 'POST'])
def speaker(flform):
    formulaire = Formulaire.query.filter_by(id=flform).first()
    if not formulaire or not formulaire.formulaire_intervenant:
        return render_template('404.html')
    evenement = formulaire.evenement
    logo0, logo, url = evenement.infos_comm()
    logofilename0, logofilename = afflogo_filter(logo0), ""
    form = IntervenantForm(formulaire)
    if form.validate_on_submit():
        personne = Personne.query.filter_by(nom=form.nom.data, prenom=form.prenom.data,
                                                    email=form.email.data).first()
        if personne == None:
            personne = Personne(nom=form.nom.data, prenom=form.prenom.data,
                                email=form.email.data)
        inscription = Inscription.query.filter_by(personne=personne, evenement=evenement)
        if inscription == None:
            inscription = Inscription(evenement=evenement, personne=personne)
        inscription.badge1 = form.badge1.data
        inscription.badge2 = form.badge2.data
        if form.telephone.data:
            inscription.telephone = form.telephone.data
        if form.fonction.data:
            inscription.fonction = form.fonction.data
        if form.organisation.data:
            inscription.organisation = form.organisation.data
        inscription.date_inscription = datetime.datetime.now()
        # Champs spéciaux intervenant
        intervenant = Intervenant(inscription=inscription)
        if form.besoin_materiel.data:
            intervenant.besoin_materiel = form.besoin_materiel.data
        if form.transport_aller.data:
            intervenant.transport_aller = form.transport_aller.data
        if form.ville_depart_aller.data:
            intervenant.ville_depart_aller = form.ville_depart_aller.data
        if form.horaire_depart_aller.data:
            intervenant.horaire_depart_aller = form.horaire_depart_aller.data
        if form.transport_retour.data:
            intervenant.transport_retour = form.transport_retour.data
        if form.ville_arrivee_retour.data:
            intervenant.ville_arrivee_retour = form.ville_arrivee_retour.data
        if form.horaire_depart_retour.data:
            intervenant.horaire_depart_retour = form.horaire_depart_retour.data
        if form.nuits.data: # booléens à attraper
            intervenant.nuits = form.nuits.data
        if form.repas.data:
            intervenant.repas = form.repas.data
        db_session.add(inscription)
        try:
            db_session.commit()
        except IntegrityError as err:
            db_session.rollback()
            flash(lazy_gettext("Erreur d'intégrité"), 'erreur')
            if "uc_intv" in str(err.orig):
                flash(lazy_gettext("Vous êtes déjà inscrit-e, comme intervenant-e, à cet événement !"), 'erreur')
        else:
            confirmer_inscription(personne.email, formulaire.evenement)
            confirmer_intervenant(personne.email, intervenant)
            flash(gettext("Votre inscription comme intervenant-e a bien été effectuée."))
            return render_template('end.html', evenement = evenement, logofilename = logofilename, lienevt = url)
    return render_template('flform.html', form=form, formulaire=formulaire, evenement=evenement, speaker=True,
                               logofilename0=logofilename0, logofilename=logofilename, url0 = url0, lienevt = url,
                               current_user=current_user)


@app.route('/suivi/new', methods=['GET', 'POST'])
@app.route('/suivi/new/', methods=['GET', 'POST'])
#@login_required
def new():
    form = NcollForm()
    form.lieu.choices = [(0, gettext('Aucun'))] + [ (l.id, l.nom) for l in Lieu.query.order_by(Lieu.nom).all()]
    if form.validate_on_submit():
        if form.uid_organisateur.data:
            uid_organisateur = form.uid_organisateur.data
        else:
            uid_organisateur = current_user.username
        evenement = Evenement(titre=form.titre.data, sstitre=form.sstitre.data,
                                  date=form.date.data, date_fin=form.date_fin.data,
                                  lieu = form.lieu.data, uid_organisateur = uid_organisateur)
        formulaire = Formulaire(evenement=evenement, date_ouverture_inscriptions = form.date_ouverture_inscriptions.data,
                                    date_cloture_inscriptions = form.date_cloture_inscriptions.data)
        if form.champ_restauration_1:
            formulaire.champ_restauration_1 = True
            formulaire.texte_restauration_1 = form.texte_restauration_1.data
        if form.champ_libre_1:
            formulaire.champ_libre_1 = True
            formulaire.texte_libre_1 = form.texte_libre_1.data
        db_session.add(evenement)
        db_session.add(formulaire)
        try:
            db_session.commit()
        except IntegrityError as err:
            db_session.rollback()
            flash(lazy_gettext("Erreur d'intégrité"), 'erreur') # sur l'événément : titre et date et organisation ?
            if "uc_even" in str(err.orig):
                flash(lazy_gettext("Vous avez déjà créé un événement à la même date, avec le même titre !"), 'erreur')
            if "uc_form" in str(err.orig):
                flash(lazy_gettext("Un formulaire existe déjà pour cet évenement, avec la même date d'ouverture des inscriptions !"), 'erreur')
        else:
            url_formulaire = request.url_root + url_for('soco', flform=formulaire.id)
            url_parts = url_formulaire . split('//') # enlever les '//' internes
            url_formulaire = url_parts[0] + '//' + '/'. join(url_parts[1:])
            flash(gettext("Votre formulaire a bien été créé."), 'info')
            flash(gettext("Voici son URL : <a href=\"" + url_formulaire + "\">" + url_formulaire + "</a>", 'url'))
            return redirect('/suivi')
    return render_template('new.html', form=form, current_user=current_user)

@app.route('/suivi')
@app.route('/suivi/')
@login_required
@required_roles('admin', 'user')
def suivi_index():
    if current_user.role == 'admin':
        evenements = Evenement.query.join("formulaire").filter(Evenement.date > datetime.datetime.now() - datetime.timedelta(days=15))
    else:
        evenements = Evenement.query.join("formulaire").filter(Evenement.uid_organisateur == current_user.username).filter(Evenement.date > datetime.datetime.now() - datetime.timedelta(days=15))
    nb_inscrits = {}
    for e in evenements:
        nb_inscrits[e.id] = len(e.inscription)
    return render_template("suivi_index.html", evenements=evenements, today=datetime.date.today(), nb_inscrits=nb_inscrits)

@app.route('/suivi/<int:evt>', methods=['GET', 'POST'])
@app.route('/suivi/<int:evt>/<action>', methods=['GET', 'POST'])
@login_required
@required_roles('admin', 'user')
def suivi(evt, action=None):
    evenement = Evenement.query.get(evt)
    if evenement == None:
        flash('Événement %d non trouvé' % evt)
        return internal_error('Evenement %d non trouvé' % evt)
    if current_user.role != 'admin' and evenement.uid_organisateur != current_user.username:
        flash('Vous n\'avez pas les droits d\'accès à cette page', 'danger')
        return redirect(url_for('index'))
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
    libre_1_existant = False
    texte_libre_1 = None
    for f in formulaires:
        if f.champ_libre_1 == True:
            libre_1_existant = True
            texte_libre_1 = f.texte_libre_1
            break
    libre_2_existant = False
    texte_libre_2 = None
    for f in formulaires:
        if f.champ_libre_2 == True:
            libre_2_existant = True
            texte_libre_2 = f.texte_libre_2
            break
    # On va chercher les inscrits
    inscrits = Inscription.query.filter_by(id_evenement=evt).all()
    # Pour les listes PDF et les badges : dans l'ordre alpha
    if action is not None and action != 'csv' and action != 'mails':
        inscrits.sort(key=lambda x: x.personne.nom)
    if action == "csv":
        csv = render_template(
            'inscrits.csv',
            evenement=evenement, inscrits=inscrits, repas_1_existant=repas_1_existant,
            texte_repas_1=texte_repas_1, repas_2_existant=repas_2_existant, texte_repas_2=texte_repas_2)
        csv_latin1 = csv#.encode("latin-1")
        response = make_response(csv_latin1)
        #response.headers["Content-Type"] = "application/csv; charset=iso-8859-15"
        response.headers["Content-Type"] = "application/csv; charset=utf-8"
        response.headers["Content-Disposition"] = "attachment; filename=inscrits-evt-%d-%s.csv" % (
            evt, datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M"))
        return response
    if action == "mails":
        return render_template('mails_inscrits.txt', inscrits = inscrits)
    if action == "listepdf":
        texcode = texenv.get_template('liste_presents.tex').render(evenement=evenement, inscrits=inscrits)
        try:
            resultat = genere_pdf(texcode)
        except:
            flash(lazy_gettext("Erreur dans la génération du document. Le plus souvent, c'est une erreur d'encodage due à un caractère inhabituel dans un nom propre"))
            return internal_error('Impossible de générer le PDF listepdf pour %d' % evt)
        if type(resultat) != type(""):
            flash(str(resultat))
            return render_template('500.html')
        return send_file(resultat, as_attachment=True, attachment_filename="presents-evt-%d-%s.pdf" % (
            evt, datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M")))
    if action == "emargement":
        texcode = texenv.get_template('liste_emargement.tex').render(evenement=evenement, inscrits=inscrits)
        resultat = genere_pdf(texcode)
        if type(resultat) != type(""):
            flash(str(resultat))
            return render_template('500.html')
        response = make_response(send_file(resultat, as_attachment=True, attachment_filename="emargement-evt-%d-%s.pdf" % (
            evt, datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M")), mimetype="application/pdf"))
        response.headers['Content-Type'] = 'application/pdf'
        return response
    if action == "badges":
        etiquettes = []
        pages_etiquettes = []
        count = 0
        base_x0, base_y0 = (0, 270)
        delta_x, delta_y = (92, 54)
        for inscrit in inscrits:
            if count > 8:
                pages_etiquettes.append(fabrique_page_etiquettes(etiquettes))
                count = 0
                etiquettes = []
            base_x = base_x0 + delta_x * (count%3)
            base_y = base_y0 - delta_y * int(count/3)
            etiquettes.append(inscrit.genere_etiquette(base_x,base_y))
            count += 1
        # Dernière page
        for i in range(count,9):
            base_x = base_x0 + delta_x * (i%3)
            base_y = base_y0 - delta_y * int(i/3)
            etiquettes.append(TPL_ETIQUETTE_VIDE % (base_x - 10, base_y + 50, base_x, base_y))
        pages_etiquettes.append(fabrique_page_etiquettes(etiquettes))
        texcode = texenv.get_template('etiquettes.tex').render(pages='\n\\newpage\n'.join(pages_etiquettes))
        resultat = genere_pdf(texcode)
        if type(resultat) != type(""):
            flash(str(resultat))
            return render_template('500.html')
        try:
            open(resultat, 'rb').read()
        except IOError as err:
            print("erreur de lecture du PDF %s" % resultat)
            flash(lazy_gettext("erreur de lecture du PDF"))
            return render_template('500.html')
        response = make_response(send_file(resultat, as_attachment=True, attachment_filename="etiquettes-evt-%d-%s.pdf" % (
            evt, datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M")), mimetype="application/pdf"))
        response.headers['Content-Type'] = 'application/pdf'
        return response
    return render_template(
        'suivi.html',
        evenement=evenement, inscrits=inscrits, repas_1_existant=repas_1_existant,
        texte_repas_1=texte_repas_1, repas_2_existant=repas_2_existant, texte_repas_2=texte_repas_2,
        avec_etiquettes=app.config['AVEC_ETIQUETTES'])


class SocoModelView(ModelView):
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
        ImageUploadField.__init__(self, label, validators, app.config['LOGO_FOLDER'], relative_path, namegen,
                                      app.config['LOGO_EXTENSIONS'], max_size, thumbgen, thumbnail_size, permission,
                                      app.config['LOGO_URL_REL'], endpoint, **kwargs)


class EvenementView(SocoModelView):
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
        lieu="Lieu de l'événement <em>(vous pouvez laisser vide s'il s'agit de la %s)</em>" % app.config['SALLE_PPALE'],
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
        'recurrence': {'label': 'Récurrence (s\'il y a lieu)'},
        'logo' : {'label': 'Logo (s\'il est différent de celui de l\'entité organisatrice)'},
        'url' : {'label': 'Lien vers la page de l\'événement'},
        'resume' : {'label': 'Résumé'},
        'gratuite' : {'label': 'Gratuité'},
        'inscription' : {'label': 'Personnes inscrites'}
        }
    form_excluded_columns = ['upd']
    form_overrides = dict(logo=LogoField)
    inline_models = [(Formulaire, dict(form_columns=['id', 'date_ouverture_inscriptions', 'date_cloture_inscriptions']))]


class FormulaireView(SocoModelView):
    column_exclude_list = ['upd', 'texte_restauration_1' , 'texte_restauration_2', 'texte_libre_1' , 'texte_libre_2']
    column_descriptions = dict(
        organisateur_en_copie = "Souhaitez-vous que l'organisateur/trice reçoive un mail à chaque inscription ?",
        champ_attestation = "Les personnes qui s'inscrivent peuvent demander une attestation de présence",
        champ_restauration_1 = "Pour pouvoir s'inscrire à un repas",
        texte_restauration_1 = "Le texte de la question correspondante",
        champ_restauration_2 = "2ème possibilité pour pouvoir s'inscrire à un repas",
        texte_restauration_2 = "Le texte de la question correspondante",
        champ_libre_1 = "Présence d'une question libre",
        texte_libre_1 = "Le texte de la cette question",
        champ_libre_2 = "Présence d'une 2ème question libre",
        texte_libre_2 = "Le texte de cette 2ème question"
        )
    form_excluded_columns = ['upd']
    form_ajax_refs = {
        'evenement': QueryAjaxModelLoader('evenement', db_session, Evenement, fields=['titre'], page_size=10)
        }
    #ajax_update = ['date_ouverture_inscriptions']


class OrganisationView(SocoModelView):
    can_export = True
    form_args = {
        'nom': {'label' : 'Nom de l\'organisation'},
        'interne' : {'label': 'Est-ce une organisation interne, susceptible d\'organiser des événements ?'},
        'email': {'label' : 'Adresse mail de contact'},
        'lieu' : {'label' : 'Lieux utilisés'},
        'evenement' : {'label' : 'Événements programmés'}
        }
    form_overrides = dict(logo=LogoField)
    #inline_models = [(Evenement, dict(form_columns=['id', 'titre', 'date']))]
    form_ajax_refs = {
        'personne': QueryAjaxModelLoader('personne', db_session, Personne, fields=['nom', 'prenom'], page_size=10),
        'lieu': QueryAjaxModelLoader('lieu', db_session, Lieu, fields=['nom'], page_size=10),
        'evenement': QueryAjaxModelLoader('evenement', db_session, Evenement, fields=['titre'], page_size=10)
        }


class LieuView(SocoModelView):
    can_export = True
    form_args = {
        'nom': {'label' : 'Nom de la salle ou du lieu'},
        'adresse' : {'label': 'Pour éviter toute ambiguïté, vous pouvez préciser l\'adresse'},
        'capacite': {'label' : 'Capacité de la salle ou du lieu (en nombre de places) ; sert à vous prévenir en cas de dépassement de capacité'},
        'evenement' : {'label' : 'Événements programmés dans ce lieu'}
        }


class PersonneView(SocoModelView):
    can_export = True
    form_args = {
        'prenom' : {'label': 'Prénom'}
    }
    inline_models = [(Inscription, dict(form_columns=['id', 'evenement', 'attestation_demandee']))]
    form_ajax_refs = {
        'organisation': QueryAjaxModelLoader('organisation', db_session, Organisation, fields=['nom'], page_size=10)
        }


class InscriptionView(SocoModelView):
    can_export = True
    form_args = {
        'telephone' : {'label': 'Téléphone'}
    }
    form_excluded_columns = ['date_inscription']
    form_ajax_refs = {
        'evenement': QueryAjaxModelLoader('evenement', db_session, Evenement, fields=['titre'], page_size=10),
        'personne': QueryAjaxModelLoader('personne', db_session, Personne, fields=['nom', 'prenom'], page_size=10)
        }


admin = Admin(app, name=app.config['NOM_INTERFACE_ADMIN'], template_mode='bootstrap3')
admin.add_view(OrganisationView(Organisation, db_session))
admin.add_view(LieuView(Lieu, db_session))
admin.add_view(EvenementView(Evenement, db_session))
admin.add_view(FormulaireView(Formulaire, db_session))
admin.add_view(PersonneView(Personne, db_session))
admin.add_view(InscriptionView(Inscription, db_session))
