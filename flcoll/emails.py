from config import ADMINS
from flcoll import mail
from flask_mail import Message
from flask import render_template
from .models import Personne, Evenement


def envoyer_message(subj, src, dest, text_body, html_body):
    msg = Message(subj, sender=src, recipients=dest)
    msg.bcc = ADMINS
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def confirmer_inscription(personne, evenement):
    envoyer_message('Confirmation d\'inscription au colloque "%s"' % evenement.titre.replace("'", "\\\'"),
                   ADMINS[0],
                   [personne.email],
                   render_template("confirmation_inscription.txt", personne=personne, evenement=evenement),
                   render_template("confirmation_inscription.html", personne=personne, evenement=evenement))
