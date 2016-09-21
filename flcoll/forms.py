from flask_wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Optional, Length, Email
from flcoll.models import Evenement, Formulaire, Personne, Inscription


class InscriptionForm(Form):
    nom = StringField('nom', validators=[DataRequired(), Length(min=2, max=30)])
    prenom = StringField('prenom', validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('email', validators=[Optional(), Email(), Length(min=0, max=70)])
    telephone = StringField('telephone', validators=[Optional(), Length(min=0, max=20)])
    #organisation = StringField('organisation', validators=[DataRequired(), Length(min=0, max=40)])
    #fonction = StringField('fonction', validators=[DataRequired(), Length(min=0, max=40)])

    def __init__(self, formulaire, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.formulaire = formulaire

    def validate(self):
        if not Form.validate(self):
            return False
        gecos = self.nom.data + " " + self.prenom.data
        if len(gecos) > 26:
            self.nom.errors.append("Attention, pour le badge, nom + prénom = 25 caractères maximum")
            self.prenom.errors.append("Attention, pour le badge, nom + prénom = 25 caractères maximum")
            return False
        return True
