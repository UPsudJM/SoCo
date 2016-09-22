from flask_wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, DateTimeField, RadioField
from wtforms.fields import Label
from wtforms.validators import DataRequired, Optional, Length, Email
from flcoll.models import Evenement, Formulaire, Personne, Inscription


class InscriptionForm(Form):
    nom = StringField('Nom', validators=[DataRequired(), Length(min=2, max=30)])
    prenom = StringField('Prénom', validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Adresse électronique', validators=[Email(), Length(min=0, max=70)])
    telephone = StringField('Téléphone', validators=[Optional(), Length(min=0, max=20)])
    organisation = StringField('Organisation', validators=[DataRequired(), Length(min=0, max=40)])
    fonction = StringField('Fonction', validators=[DataRequired(), Length(min=0, max=40)])
    attestation_demandee = BooleanField('Cochez cette case si vous désirez-vous une attestation de présence')
    type_inscription = RadioField('Type d\'inscription', choices=[("presence","Vous assisterez au colloque"), ("interet","Vous n'assisterez pas au colloque, mais souhaitez établir un contact pour recevoir de l'information sur le sujet")])
    inscription_repas_1 = BooleanField('Repas 1')
    inscription_repas_2 = BooleanField('Repas 2')

    def __init__(self, formulaire, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
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
        if not Form.validate(self):
            return False
        if len(self.nom.data) + len(self.prenom.data) > 26:
            self.nom.errors.append("Attention, pour le badge, nom + prénom = 26 caractères maximum")
            self.prenom.errors.append("Attention, pour le badge, nom + prénom = 26 caractères maximum")
            return False
        return True
