# coding: utf-8
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

import datetime, locale, os
from PIL import Image
from sqlalchemy.exc import IntegrityError
#from config import LANGUAGES
from flask import render_template, flash, redirect, make_response, session, url_for, request, g, send_file, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin.form.upload import ImageUploadField
from flask_babelex import gettext, lazy_gettext
from soco import app, babel, db_session, lm, LOGO_DEFAULT, URL_DEFAULT
from wtforms.validators import DataRequired
from functools import wraps
from .auth.models import User
from .models import Organisation, Lieu, Evenement, Recurrent, Formulaire, Personne, Inscription, Intervenant
from .forms import InscriptionForm, FormulaireForm, IntervenantForm
from .filters import localedate_filter, localedatetime_filter, datedebut_filter, datedebutcompl_filter
from .emails import confirmer_inscription, envoyer_mail_capacite_salle
from .texenv import texenv, genere_pdf, TPL_ETIQUETTE_VIDE, fabrique_page_etiquettes


@babel.localeselector
def get_locale():
    locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')
    return "fr"
    #return request.accept_languages.best_match(LANGUAGES.keys())

def get_current_user_id():
    return current_user.id

def get_current_user_role():
    return current_user.role.name

def get_current_user_events():
    try:
        ids_evenements_autorises_tuples = db_session.execute(
            "SELECT id_evenement FROM evenement_organisateur, utilisateur WHERE id_organisateur=id\
            and id_organisateur=" + current_user.get_id()
        ).fetchall()
        ids_evenements_autorises = [ e[0] for e in ids_evenements_autorises_tuples ]
    except:
        ids_evenements_autorises = []
        flash(gettext('Une erreur est survenue dans l\'accès à la liste des événements'),'error')
    return ids_evenements_autorises

def get_current_user_forms():
    try:
        ids_formulaires_autorises_tuples = db_session.execute(
            "SELECT formulaire.id FROM formulaire, evenement_organisateur, utilisateur \
            WHERE id_organisateur=utilisateur.id AND id_organisateur=%s \
            AND formulaire.id_evenement=evenement_organisateur.id_evenement" % get_current_user_id()
        ).fetchall()
        ids_formulaires_autorises = [ f[0] for f in ids_formulaires_autorises_tuples ]
    except:
        ids_formulaires_autorises = []
        flash(gettext('Une erreur est survenue dans l\'accès à la liste des formulaires'),'error')
    return ids_formulaires_autorises

def required_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if get_current_user_role() not in roles and not current_user.is_admin:
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

def afflogo(f, size=(64,64)):
    infile = app.config['LOGO_FOLDER'] + f
    thumbnail = "petit-" + f
    outfile = app.config['LOGO_FOLDER'] + thumbnail
    try:
        im = Image.open(outfile)
    except IOError:
        try:
            im = Image.open(infile)
            im.thumbnail(size)
            im.save(outfile, "PNG")
        except IOError:
            print("cannot create thumbnail for", f)
    finally:
        return app.config['LOGO_URL_REL'] + thumbnail

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db_session.rollback()
    return render_template('500.html'), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
@app.route('/index')
# ECRIRE LES RESTRICTIONS DANS LA FONCTION
def index():
    logo = LOGO_DEFAULT
    logofilename = afflogo(logo)
    evenements = Evenement.query.all()
    return render_template('index.html', title='Conferences', logofilename=logofilename, evenements=evenements)

@app.route('/colloque/<int:flform>', methods=['GET', 'POST'])
@app.route('/event/<int:flform>', methods=['GET', 'POST'])
@app.route('/speaker/<int:flform>/<token>', methods=['GET', 'POST'])
def soco(flform, token=None):
    formulaire = Formulaire.query.filter_by(id=flform).first()
    if not formulaire:
        return render_template('404.html')
    evenement = formulaire.evenement
    # Vérification pour le cas 'Intervenant'
    speaker = False
    if token:
        intervenant = Intervenant.check_token(evenement.id, token)
        if intervenant:
            speaker = True
    # Choix des logos
    logo, url = evenement.infos_comm()
    if evenement.entite_organisatrice:
        logo0, url0 = evenement.entite_organisatrice.infos_comm()
        if logo0 == logo:
            logo0 = LOGO_DEFAULT
        if url0 == url:
            url0 = URL_DEFAULT
    else:
        logo0, url0 = LOGO_DEFAULT, URL_DEFAULT
    logofilename0, logofilename = afflogo(logo0), ""
    if logo:
        logofilename = afflogo(logo)
    if speaker:
        form = IntervenantForm(formulaire)
        deja_personne = intervenant.inscription.personne
        inscription = intervenant.inscription
    else:
        # avant ou après l'heure, ce n'est pas l'heure de s'inscrire. Sauf pour les responsables d'événements
        if formulaire.date_cloture_inscriptions < datetime.date.today():
            return render_template('erreur.html', msg=gettext('Les inscriptions pour cet événement sont closes !'))
        elif formulaire.date_ouverture_inscriptions > datetime.date.today()  and not formulaire.id in get_current_forms():
            return render_template('erreur.html', msg=gettext('Les inscriptions pour cet événement ne sont pas encore ouvertes !'))
        form = InscriptionForm(formulaire)
        deja_personne = None
        inscription = None
    if form.validate_on_submit():
         # FIXME mieux gérer le cas où la personne (intervenant) a modifié les infos ci-dessous
        personne = Personne.query.filter_by(nom=form.nom.data, prenom=form.prenom.data,
                                                    email=form.email.data).first()
        if personne == None:
            personne = Personne(nom=form.nom.data, prenom=form.prenom.data,
                                email=form.email.data)
        if inscription == None:
            inscription = Inscription(evenement=evenement, personne=personne)
            inscription.genere_token()
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
        jours_de_presence = None
        if form.jours_de_presence.data:
            jours_de_presence = []
            for k, v in request.values.items():
                if k[:4] == "jour":
                    jours_de_presence.append(k[5:])
            inscription.jours_de_presence = ' '. join(jours_de_presence)
        if formulaire.champ_restauration_1 and form.inscription_repas_1.data:
            inscription.inscription_repas_1 = form.inscription_repas_1.data
        if formulaire.champ_restauration_2 and form.inscription_repas_2.data:
            inscription.inscription_repas_2 = form.inscription_repas_2.data
        if formulaire.champ_libre_1 and form.reponse_question_1.data:
            inscription.reponse_question_1 = form.reponse_question_1.data
        if formulaire.champ_libre_2 and form.reponse_question_2.data:
            inscription.reponse_question_2 = form.reponse_question_2.data
        db_session.add(inscription)
        if speaker:
            for attrname in ['besoin_materiel', 'transport_aller', 'ville_depart_aller', 'horaire_depart_aller', 'transport_retour', 'ville_arrivee_retour', 'horaire_depart_retour']:
                field = getattr(form, attrname)
                if field.data:
                    setattr(intervenant, attrname, field.data)
            hebergements = []
            for k, v in request.values.items():
                if k[:4] in ['nuit', 'midi', 'soir'] and v == 'on':
                    hebergements.append(k)
            intervenant.hebergements = ' '. join(hebergements)
            db_session.add(intervenant)
            print("intervenant=", intervenant)
        try:
            db_session.commit()
        except IntegrityError as err:
            db_session.rollback()
            if speaker:
                flash(lazy_gettext("Erreur d'intégrité"), 'erreur')
                if "uc_intv" in str(err.orig):
                    flash(lazy_gettext("Vous avez déjà fourni vos informations !"), 'erreur')
            else:
                flash(lazy_gettext("Erreur d'intégrité"), 'erreur')
                if "uc_porg" in str(err.orig):
                    flash(lazy_gettext("Vous vous êtes déjà inscrit-e avec ces mêmes nom, prénom et organisation !"), 'erreur')
                if "uc_pers" in str(err.orig):
                    flash(lazy_gettext("Vous vous êtes déjà inscrit-e avec ces mêmes nom, prénom et adresse électronique !"), 'erreur')
                if "uc_insc" in str(err.orig):
                    flash(lazy_gettext("Vous êtes déjà inscrit-e à cet événement !"), 'erreur')
        else:
            confirmer_inscription(personne.email, formulaire.evenement, jours=jours_de_presence)
            nb_inscrits = len(evenement.inscription)
            capacite_lieu = evenement.lieu.capacite
            if capacite_lieu and capacite_lieu > 0:
                pourcentage_anterieur = ( nb_inscrits - 1 )* 100 / capacite_lieu
                pourcentage = nb_inscrits * 100 / capacite_lieu
                if (pourcentage_anterieur < 80 and pourcentage >= 80) \
                  or (pourcentage_anterieur < 90 and pourcentage >= 90) \
                  or (pourcentage_anterieur < 100 and pourcentage >= 100) \
                  or (pourcentage_anterieur < 110 and pourcentage >= 110) \
                  or (pourcentage_anterieur < 120 and pourcentage >= 120) \
                  or (pourcentage_anterieur < 150 and pourcentage >= 150) \
                  or (pourcentage_anterieur < 200 and pourcentage >= 200):
                    envoyer_mail_capacite_salle(formulaire.evenement, nb_inscrits, capacite_lieu)
            if speaker:
                flash(gettext("Vos informations ont bien été enregistrées."))
            else:
                flash(gettext("Votre inscription a bien été effectuée."))
            if app.config['AVEC_QRCODE']:
                flash(gettext("Ce code graphique vous permettra d'entrer sur les lieux de l'événement, conservez-le !"))
                url_verif = app.config['URL_APPLICATION'] + '/verif/%s/%s' % (evenement.id, inscription.token)
                qrstring = gettext("SoCo - Événement {evt} : {prenom} {nom} est inscrit-e sous le numéro {num}.\n{url}").format(
                    evt = evenement.titre, prenom = personne.prenom, nom = personne.nom, num = inscription.id, url=url_verif)
                print(qrstring)
            else:
                qrstring = ''
            return render_template('end.html', evenement=evenement, logofilename=logofilename,
                                   qrstring=qrstring, lienevt=url)
    return render_template('flform.html', form=form, formulaire=formulaire, evenement=evenement, speaker=speaker,
                           intervenant=deja_personne,
                           logofilename0=logofilename0, logofilename=logofilename, url0=url0, lienevt=url,
                           current_user=current_user)


@app.route('/end')
def end():
    id_evenement = session.id_evenement
    evenement = Evenement.query.filter_by(id=id_evenement).first()
    return render_template('end.html', evenement=evenement, logofilename=session.logofilename)

@app.route('/verif/<evt>/<token>')
@login_required
@required_roles('admin', 'user')
def verif(evt, token):
    evenement = Evenement.query.get(evt)
    logo, url = evenement.infos_comm()
    if not logo:
        logo = app.config['LOGO_DEFAULT']
    logofilename = afflogo(logo)
    inscription = Inscription.query.filter_by(token=token).first()
    if not inscription:
        return render_template('verif.html', ok=False, title=gettext("Vérification d'une inscription"), logofilename=logofilename,
                               evenement=evenement)
    if inscription.evenement.id != int(evt):
        return render_template('verif.html', ok=False, logofilename=logofilename)
    return render_template('verif.html', ok=True, title=gettext("Vérification d'une inscription"), logofilename=logofilename,
                           personne=inscription.personne, evenement=inscription.evenement)

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


@app.route('/suivi/new', methods=['GET', 'POST'])
@app.route('/suivi/new/', methods=['GET', 'POST'])
@app.route('/suivi/edit/<formulaire_id>', methods=['GET', 'POST'])
@login_required
def new(formulaire_id=None):
    if formulaire_id:
        # Édition d'un formulaire déjà créé
        formulaire = Formulaire.query.get(formulaire_id)
        # Vérifier qu'on a bien les droits
        if int(formulaire_id) in get_current_user_forms():
            form = FormulaireForm(obj=formulaire)
            if formulaire.evenement.lieu:
                form.evenement.lieu.data = formulaire.evenement.id_lieu
            if formulaire.evenement.organisateurs:
                form.evenement.organisateurs.data = [ u.id for u in formulaire.evenement.organisateurs ]
            print(form.data)
        else:
            flash(gettext('Vous n\'avez pas les droits d\'accès à cette page'),'error')
            form = FormulaireForm()
    else:
        # Formulaire tout neuf
        form = FormulaireForm()
    if form.validate_on_submit():
        if form.evenement.organisateurs.data:
            organisateurs = [ User.query.get(ident) for ident in form.evenement.organisateurs.data ]
        else:
            form.evenement.organisateurs.data = [ current_user.id ]
            organisateurs = [ current_user ]
        if form.evenement.lieu.data:
            lieu = Lieu.query.get(form.evenement.lieu.data)
        else:
            lieu = None
        if formulaire_id:
            formulaire.evenement.titre = form.evenement.titre.data
            formulaire.evenement.sstitre = form.evenement.sstitre.data
            formulaire.evenement.date = form.evenement.date.data
            formulaire.evenement.date_fin = form.evenement.date_fin.data
            formulaire.evenement.recurrence = form.evenement.recurrence.data
            formulaire.evenement.lieu = lieu
            formulaire.evenement.organisateurs = organisateurs
            formulaire.date_ouverture_inscriptions = form.date_ouverture_inscriptions.data
            formulaire.date_cloture_inscriptions = form.date_cloture_inscriptions.data
        else:
            evenement = Evenement(titre=form.evenement.titre.data, sstitre=form.evenement.sstitre.data, date=form.evenement.date.data,
                                    date_fin=form.evenement.date_fin.data, recurrence=form.evenement.recurrence.data, lieu=lieu)
            evenement.organisateurs = organisateurs
            formulaire = Formulaire(evenement=evenement, date_ouverture_inscriptions = form.date_ouverture_inscriptions.data,
                                    date_cloture_inscriptions = form.date_cloture_inscriptions.data)
        if form.champ_restauration_1.data:
            formulaire.champ_restauration_1 = True
            formulaire.texte_restauration_1 = form.texte_restauration_1.data
        else:
            formulaire.champ_restauration_1 = False
            formulaire.texte_restauration_1 = None
        if form.champ_libre_1.data:
            formulaire.champ_libre_1 = True
            formulaire.texte_libre_1 = form.texte_libre_1.data
        else:
            formulaire.champ_libre_1 = False
            formulaire.texte_libre_1 = None
        if formulaire.evenement.recurrence:
            formulaire.evenement.calcule_recurrence()
            formulaire.jour_par_jour = True
        db_session.add(formulaire)
        try:
            db_session.commit()
        except IntegrityError as err:
            db_session.rollback()
            flash(lazy_gettext("Un événement a déjà été créé de même date et même titre"), 'erreur') # unicité titre + date + organisation
            if "uc_even" in str(err.orig):
                flash(lazy_gettext("Vous avez déjà créé un événement à la même date, avec le même titre !"), 'erreur')
            if "uc_form" in str(err.orig):
                flash(lazy_gettext("Un formulaire existe déjà pour cet évenement, avec la même date d'ouverture des inscriptions !"), 'erreur')
        else:
            url_formulaire = request.url_root + url_for('soco', flform=formulaire.id)
            url_parts = url_formulaire . split('//') # enlever les '//' internes
            url_formulaire = url_parts[0] + '//' + '/'. join(url_parts[1:])
            if formulaire_id:
                flash(gettext("Votre formulaire a bien été modifié."), 'info')
            else:
                flash(gettext("Votre formulaire a bien été créé."), 'info')
            flash(gettext("Voici son URL : <a href=\"" + url_formulaire + "\">" + url_formulaire + "</a>"), 'url')
            return redirect(url_for('suivi_index'))
    return render_template('new.html', form=form, avec_recurrence=app.config['AVEC_RECURRENCE'], formulaire_id=formulaire_id,
                               current_user=current_user)

@app.route('/suivi')
@app.route('/suivi/index')
@login_required
@required_roles('admin', 'user')
def suivi_index():
    if current_user.is_admin:
        evenements = Evenement.query.join("formulaire").filter(Evenement.date > datetime.datetime.now() - datetime.timedelta(days=15))
    else:
        ids_evenements_autorises = get_current_user_events()
        evenements_en_cours = Evenement.query.join("formulaire").filter(Evenement.date > datetime.datetime.now() - datetime.timedelta(days=15))
        evenements = [ e for e in evenements_en_cours if e.id in ids_evenements_autorises ]
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
    if not current_user.is_admin and not current_user in evenement.organisateurs:
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
        avec_etiquettes=app.config['AVEC_ETIQUETTES'], today=datetime.date.today())


class SocoModelView(ModelView):
    __abstract__ = True
    form_excluded_columns = ['upd']

    def is_accessible(self):
        try:
            return current_user.is_admin
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
    column_labels = dict(sstitre = gettext('Sous-titre'), date = gettext('Date'), organisateurs = gettext('Organisé par'),
                             resume = gettext('Résumé'), gratuite = gettext('Gratuité'), recurrence = gettext('Récurrence'),
                             entite_organisatrice = gettext('Entité organisatrice'), upd = gettext('Mis à jour le'))
    column_choices = {'gratuite': [ (True, 'oui'), (False, 'non') ] }
    column_exclude_list = ['upd', 'resume']
    column_sortable_list = ['titre', 'date', 'organisateurs']
    column_filters = ['titre', 'lieu', 'organisateurs', 'gratuite']
    column_default_sort = 'date'
    column_descriptions = dict(
        titre = gettext('Titre de l\'événement'),
        sstitre = gettext('Sous-titre de l\'événement'),
        lieu = gettext("Lieu de l'événement <em>(vous pouvez laisser vide s'il s'agit de la {salle_ppale})</em>").format(
            salle_ppale = app.config['SALLE_PPALE']),
        organisateurs = gettext('Les organisateurs'),
        gratuite = gettext('L\'entrée est-elle libre ?')
        )
    #column_formatters = dict(date=lambda v, c, m, p: m.date.date(),
    #                             date_fin=lambda v, c, m, p: (m.date_fin and m.date_fin!=m.date and m.date_fin.date()) or "",
    #                             )
    form_args = {
        'titre': {'label': gettext('Titre'), 'validators': [DataRequired()]},
        'sstitre': {'label': gettext('Sous-titre')},
        'date': {'label': gettext('Date'), 'validators': [DataRequired()]},
        'date_fin': {'label': gettext('Date de fin (si nécessaire)')},
        'recurrence': {'label': gettext('Récurrence')},
        'logo' : {'label': gettext('Logo (s\'il est différent de celui de l\'entité organisatrice)')},
        'url' : {'label': gettext('Lien vers la page de l\'événement')},
        'resume' : {'label': gettext('Résumé')},
        'gratuite' : {'label': gettext('Gratuité')},
        'inscription' : {'label': gettext('Personnes inscrites')},
        'recurrent' : {'label': gettext('Date supplémentaire (cas évt récurrent)')}
        }
    form_overrides = dict(logo=LogoField)
    inline_models = [(Formulaire, dict(form_columns=['id', 'date_ouverture_inscriptions', 'date_cloture_inscriptions']))]
    #if app.config['AVEC_RECURRENCE']:
    inline_models.append((Recurrent, dict(form_columns=['id', 'date'])))


class FormulaireView(SocoModelView):
    column_exclude_list = ['upd', 'texte_restauration_1' , 'texte_restauration_2', 'texte_libre_1' , 'texte_libre_2']
    column_labels = dict(
        date_ouverture_inscriptions = gettext("Ouverture inscript."),
        date_cloture_inscriptions = gettext("Clôture inscript.")
        )
    column_descriptions = dict(
        organisateurs_en_copie = gettext("Souhaitez-vous que les organisateurs reçoivent un mail à chaque inscription ?"),
        champ_attestation = gettext("Les personnes qui s'inscrivent peuvent demander une attestation de présence"),
        champ_restauration_1 = gettext("Pour pouvoir s'inscrire à un repas"),
        texte_restauration_1 = gettext("Le texte de la question correspondante"),
        champ_restauration_2 = gettext("2ème possibilité pour pouvoir s'inscrire à un repas"),
        texte_restauration_2 = gettext("Le texte de la question correspondante"),
        champ_libre_1 = gettext("Présence d'une question libre"),
        texte_libre_1 = gettext("Le texte de la cette question"),
        champ_libre_2 = gettext("Présence d'une 2ème question libre"),
        texte_libre_2 = gettext("Le texte de cette 2ème question")
        )
    form_ajax_refs = {
        'evenement': QueryAjaxModelLoader('evenement', db_session, Evenement, fields=['titre'], page_size=10)
        }
    form_args = {
        'date_ouverture_inscriptions': {'label': gettext('Date d\'ouverture des inscriptions'), 'validators': [DataRequired()]},
        'date_cloture_inscriptions': {'label': gettext('Date de clôture des inscriptions'), 'validators': [DataRequired()]},
        'organisateurs_en_copie' : {'label': gettext('Organisateurs en copie ?')}
        }
    #ajax_update = ['date_ouverture_inscriptions']


class OrganisationView(SocoModelView):
    can_export = True
    form_args = {
        'nom': {'label' : gettext('Nom de l\'organisation')},
        'interne' : {'label': gettext('Est-ce une organisation interne, susceptible d\'organiser des événements ?')},
        'email': {'label' : gettext('Adresse mail de contact')},
        'lieu' : {'label' : gettext('Lieux utilisés')},
        'evenement' : {'label' : gettext('Événements programmés')}
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
        'nom': {'label' : gettext('Nom de la salle ou du lieu')},
        'adresse' : {'label': gettext('Pour éviter toute ambiguïté, vous pouvez préciser l\'adresse')},
        'capacite': {'label' : gettext('Capacité de la salle ou du lieu (en nombre de places) ; sert à vous prévenir en cas de dépassement de capacité')},
        'evenement' : {'label' : gettext('Événements programmés dans ce lieu')}
        }


class PersonneView(SocoModelView):
    can_export = True
    column_exclude_list = ['token']
    form_args = {
        'prenom' : {'label': gettext('Prénom')}
    }
    inline_models = [(Inscription, dict(form_columns=['id', 'evenement', 'attestation_demandee']))]
    form_ajax_refs = {
        'organisation': QueryAjaxModelLoader('organisation', db_session, Organisation, fields=['nom'], page_size=10)
        }


class InscriptionView(SocoModelView):
    can_export = True
    column_exclude_list = ['upd', 'token', 'type_inscription', 'telephone', 'commentaire', 'badge1', 'badge2']
    form_args = {
        'telephone' : {'label': gettext('Téléphone')}
    }
    form_ajax_refs = {
        'evenement': QueryAjaxModelLoader('evenement', db_session, Evenement, fields=['titre'], page_size=10),
        'personne': QueryAjaxModelLoader('personne', db_session, Personne, fields=['nom', 'prenom'], page_size=10)
        }


class IntervenantView(SocoModelView):
    can_export = True
    form_args = {
        'besoin_materiel' : {'label': gettext('Besoin matériel')},
        'transport_aller' : {'label': gettext('Transport aller')},
        'ville_depart_aller' : {'label': gettext('Ville de départ (aller)')},
        'horaire_depart_aller' : {'label': gettext('Horaire de départ (aller)')},
        'transport_retour' : {'label': gettext('Transport retour')},
        'ville_arrivee_retour' : {'label': gettext('Ville de destination (retour)')},
        'horaire_depart_retour' : {'label': gettext('Horaire de départ (retour)')},
        'hebergements' : {'label': gettext('Hébergements à prévoir')}
  }


admin = Admin(app, name=app.config['NOM_INTERFACE_ADMIN'], template_mode='bootstrap3')
admin.add_view(OrganisationView(Organisation, db_session))
admin.add_view(LieuView(Lieu, db_session))
admin.add_view(EvenementView(Evenement, db_session))
admin.add_view(FormulaireView(Formulaire, db_session))
admin.add_view(PersonneView(Personne, db_session))
admin.add_view(InscriptionView(Inscription, db_session))
admin.add_view(IntervenantView(Intervenant, db_session))
