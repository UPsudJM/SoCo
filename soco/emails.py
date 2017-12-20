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

from config import ADMINS, MAIL_DOMAIN, EMAIL_SITE, URL_APPLICATION
if not ADMINS:
    ADMINS = [ EMAIL_SITE ]
from soco import mail
from .models import Evenement
from flask_mail import Message
from flask import render_template
from flask_babelex import gettext, lazy_gettext


def formatte_emails(emails_possiblement_incomplets):
    """On part du principe que souvent, les emails se calculent à partir des uids"""
    ret = []
    for e in emails_possiblement_incomplets:
        if '@' in e:
            ret.append(e)
        else:
            if not MAIL_DOMAIN:
                continue
            ret.append(e + '@' + MAIL_DOMAIN)

def envoyer_message(subj, src, dest, text_body, html_body):
    def complete_mail(adresse):
        if not '@' in adresse:
            adresse = adresse + '@' + MAIL_DOMAIN
    msg = Message(subj, sender=src, recipients=[ complete_mail(a) for a in dest ])
    msg.bcc = ADMINS
    msg.body = text_body
    msg.html = html_body
    try:
        mail.send(msg)
    except:
        print("Erreur: impossible d'envoyer le mail")


def confirmer_inscription(email, evenement):
    envoyer_message(gettext('SoCo : Confirmation d\'inscription à "{titre}"').format(titre=evenement.titre.replace("'", "\\\'")),
        EMAIL_SITE,
        [email],
        render_template("confirmation_inscription.txt", evenement=evenement),
        render_template("confirmation_inscription.html", evenement=evenement))

def envoyer_code_verification(email):
    from random import shuffle
    l = ['0','1','2','3','4','5','6','7','8','9']
    shuffle(l)
    codeverif = "".join(l[:4])
    envoyer_message('SoCo : Votre code de vérification',
                        ADMINS[0],
                        [email],
                        render_template("envoi_code_verification.txt", codeverif=codeverif),
                        render_template("envoi_code_verification.html", codeverif=codeverif))
    return codeverif

def envoyer_mail_modification_formulaire(emails, evenement, **kwargs):
    lignes_info = []
    from .forms import NcollForm
    for k, v in kwargs.items():
        try:
            libelle = getattr(NcollForm, k).args[0]
        except:
            libelle = k
        lignes_info.append(lazy_gettext("Nouvelle valeur de {libelle} : {val}").format(libelle=libelle, val=v))
    envoyer_message(lazy_gettext('SoCo : Votre formulaire a été modifié'),
                        ADMINS[0],
                        formatte_emails(emails),
                        render_template("envoi_mail_modification_formulaire.txt",
                                            evenement = evenement, lignes_info=lignes_info),
                        render_template("envoi_mail_modification_formulaire.html",
                                            evenement = evenement, lignes_info=lignes_info))

def envoyer_mail_capacite_salle(emails_or_uids_organisateurs, evenement, nb_inscrits, capacite_lieu=None, **kwargs):
    if not capacite_lieu:
        capacite_lieu = evenement.lieu.capacite
    emails_organisateurs = formatte_emails(emails_or_uids_organisateurs)
    envoyer_message(lazy_gettext('SoCo : Information sur les inscriptions à "{titre}"').format(titre=evenement.titre),
                        ADMINS[0],
                        emails_organisateurs,
                        render_template("envoi_mail_capacite_salle.txt",
                                            evenement = evenement, nb_inscrits=nb_inscrits, capacite_lieu=capacite_lieu),
                        render_template("envoi_mail_capacite_salle.html",
                                            evenement = evenement, nb_inscrits=nb_inscrits, capacite_lieu=capacite_lieu)
                                            )

def envoyer_invitation_intervenant(evenement, emails_or_uids_organisateurs, email_interv, code_interv, msg=None, **kwargs):
    emails_organisateurs = formatte_emails(emails_or_uids_organisateurs)
    lien = "{url_app}/speaker/{evt}/{code}".format(url_app=URL_APPLICATION, evt=evenement.id, code=code_interv)
    envoyer_message(lazy_gettext('SoCo : Invitation à intervenir à "{titre}"').format(titre=evenement.titre),
                        ADMINS[0],
                        email_interv,
                        # FIXME positionner Cc: et Reply-to:
                        render_template("envoi_invitation_intervenant.txt", evenement=evenement, msg=msg, lien=lien),
                        render_template("envoi_invitation_intervenant.html", evenement=evenement, msg=msg, lien=lien)
                        )
