from flask_wtf import FlaskForm
from flask import flash
from wtforms import StringField, BooleanField, TextAreaField, RadioField, DateField
from wtforms.fields import Label
from wtforms.validators import DataRequired, Optional, Length, Email
from soco.models import Evenement, Formulaire, Personne, Inscription
import datetime


class SocoForm(FlaskForm):
    def flash_errors(self):
        for field, errors in self.errors.items():
            for error in errors:
                flash(u"Error in the %s field - %s" % (getattr(self, field).label.text, error))


class NcollForm(SocoForm):
    titre = StringField('Titre', validators=[DataRequired(), Length(min=3, max=300)])
    sstitre = StringField('Sous-titre')
    date = DateField('Date', format='%d/%m/%Y', validators=[DataRequired()])
    date_fin = DateField('Date de fin', format='%d/%m/%Y', description="cas où l'événement dure plusieurs jours")
    lieu = StringField('Lieu', description="si laissé vide : salle Georges Vedel à la Faculté Jean Monnet")
    date_ouverture_inscriptions = DateField("Date d'ouverture des inscriptions", format='%d/%m/%Y', validators=[DataRequired()])
    date_cloture_inscriptions = DateField("Date de clôture des inscriptions", format='%d/%m/%Y', validators=[DataRequired()])
    champ_restauration_1 = BooleanField("Champ restauration 1")
    texte_restauration_1 = StringField("Texte restauration 1")

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        print(self.date_ouverture_inscriptions)
        print(dir(self.date_ouverture_inscriptions))
        if self.date_ouverture_inscriptions.data > self.date_cloture_inscriptions.data:
            self.date_ouverture_inscriptions.errors.append("La date d'ouverture ne peut pas être antérieur à la date de clôture")
            return False
        if (self.date_fin.data and self.date_cloture_inscriptions.data > self.date_fin.data) \
          or (not self.date_fin.data and self.date_cloture_inscriptions.data > self.date.data):
            self.date_ouverture_inscriptions.errors.append("La date de clôture ne peut pas être postérieure à la date de l'événement")
            return False
        auj = datetime.date.today()
        if not self.date_ouverture_inscriptions.data or self.date_ouverture_inscriptions.data < auj:
            self.date_ouverture_inscriptions.data = auj
        return True


class InscriptionForm(SocoForm):
    nom = StringField('Nom', validators=[DataRequired(), Length(min=2, max=30)])
    prenom = StringField('Prénom', validators=[Optional(), Length(min=2, max=30)], description="Attention, pour le badge : prénom + nom = 26 caractères max.")
    email = StringField('Adresse électronique', validators=[DataRequired(), Email(), Length(min=0, max=70)])
    telephone = StringField('Téléphone', validators=[Optional(), Length(min=0, max=20)])
    organisation = StringField('Organisation', validators=[DataRequired(), Length(min=0, max=40)], description="Attention, pour le badge : fonction + organisation = 32 caractères max.")
    fonction = StringField('Fonction', validators=[Optional(), Length(min=0, max=40)])
    badge1 = StringField('Badge1', validators=[DataRequired(), Length(min=1, max=27)])
    badge2 = StringField('Badge2', validators=[DataRequired(), Length(min=1, max=33)])
    attestation_demandee = BooleanField('Cochez cette case si vous désirez une attestation de présence&nbsp;:')
    type_inscription = RadioField('Type d\'inscription', choices=[("presence","Vous assisterez au colloque"), ("interet","Vous n'assisterez pas au colloque, mais souhaitez établir un contact pour recevoir de l'information sur le sujet")])
    inscription_repas_1 = BooleanField('Repas 1')
    inscription_repas_2 = BooleanField('Repas 2')

    def __init__(self, formulaire, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.formulaire = formulaire
        if not formulaire.champ_attestation:
            self.__delitem__('attestation_demandee')
        if not formulaire.champ_type_inscription:
            self.__delitem__('type_inscription')
        if formulaire.champ_restauration_1:
            self.__getitem__('inscription_repas_1').label = Label('inscription_repas_1', formulaire.texte_restauration_1)
        else:
            self.__delitem__('inscription_repas_1')
        if formulaire.champ_restauration_2:
            self.__getitem__('inscription_repas_2').label = Label('inscription_repas_1', formulaire.texte_restauration_2)
        else:
            self.__delitem__('inscription_repas_2')

    def validate(self):
        if not FlaskForm.validate(self):
            self.flash_errors()
            return False
        return True