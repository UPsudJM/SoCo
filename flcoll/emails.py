from config import ADMINS
from flcoll import mail
from flask_mail import Message
from flask import render_template


def envoyer_message(subj, src, dest, text_body, html_body):
    msg = Message(subj, sender=src, recipients=dest)
    msg.bcc = ADMINS
    msg.body = text_body
    msg.html = html_body
    try:
        mail.send(msg)
    except SMTPError:
        print("Erreur: impossible d'envoyer le mail")


def confirmer_inscription(email, evenement):
    from .models import Evenement
    envoyer_message('Soco : Confirmation d\'inscription au colloque "%s"' % evenement.titre.replace("'", "\\\'"),
                   ADMINS[0],
                   [email],
                   render_template("confirmation_inscription.txt", evenement=evenement),
                   render_template("confirmation_inscription.html", evenement=evenement))

def envoyer_code_verification(email):
    from random import shuffle
    l = ['0','1','2','3','4','5','6','7','8','9']
    shuffle(l)
    codeverif = "".join(l[:4])
    envoyer_message('Soco : Votre code de vérification',
                        ADMINS[0],
                        [email],
                        render_template("envoi_code_verification.txt", codeverif=codeverif),
                        render_template("envoi_code_verification.html", codeverif=codeverif))
    return codeverif

def envoyer_mail_modification_formulaire(email, **kwargs):
    lignes_info = []
    for k, v in kwargs:
        lignes_info.append("Nouvelle valeur de %s : %s" % (k, w))
    envoyer_message('Soco : Votre formulaire a été modifié',
                        ADMINS[0],
                        [email],
                        render_template("envoi_mail_modification_formulaire.txt", lignes_info=lignes_info),
                        render_template("envoi_mail_modification_formulaire.html", lignes_info=lignes_info))
