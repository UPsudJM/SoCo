from flask_wtf import FlaskForm
from flask import flash
from wtforms import StringField, BooleanField, TextAreaField, RadioField, DateField
from wtforms.fields import Label
from wtforms.validators import DataRequired, Optional, Length, Email
from soco.models import Evenement, Formulaire, Personne, Inscription
from soco import app
import datetime


class ClickStringField(StringField):
    def __init__(self, *args, **kwargs):
        objname = None
        if 'objname' in kwargs.keys():
            objname = kwargs['objname']
            del kwargs['objname']
        defaultvalue = None
        if 'defaultvalue' in kwargs.keys():
            defaultvalue = kwargs['defaultvalue']
            del kwargs['defaultvalue']
        clickfunc = None
        if 'clickfunc' in kwargs.keys():
            clickfunc = kwargs['clickfunc']
            del kwargs['clickfunc']
        super(ClickStringField, self).__init__(*args, **kwargs)
        if objname:
            self.ng_model = objname + '.' + self.name
        elif self.name:
            self.ng_model = self.name
        else:
            self.ng_model = None
        if defaultvalue:
            self.defaultvalue = defaultvalue
        else:
            self.defaultvalue = None
        if clickfunc:
            self.ng_click = clickfunc
        elif self.name:
            self.ng_click = "click_" + self.name
        else:
            self.ng_click = None

    def __call__(self, **kwargs):
        if hasattr(self, 'ng_model'):
            kwargs['ng-model'] = self.ng_model
        if hasattr(self, 'ng_click'):
            kwargs['ng-click'] = self.ng_click + '()'
        if hasattr(self, 'defaultvalue'):
            kwargs['defaultvalue'] = self.defaultvalue
        return super(ClickStringField, self).__call__(**kwargs)


class PickaDateField(DateField):
    def __init__(self, *args, **kwargs):
        objname = None
        if 'objname' in kwargs.keys():
            objname = kwargs['objname']
            del kwargs['objname']
        changefunc = None
        if 'changefunc' in kwargs.keys():
            changefunc = args['changefunc']
            del args['changefunc']
        super(PickaDateField, self).__init__(*args, **kwargs)
        if objname:
            self.ng_model = objname + '.' + self.name
        elif self.name:
            self.ng_model = self.name
        else:
            self.ng_model = None
        if changefunc:
            self.ng_change = changefunc
        elif self.name:
            self.ng_change = "calc_" + self.name
        else:
            self.ng_change = None

    def __call__(self, **kwargs):
        if hasattr(self, 'ng_model'):
            kwargs['ng-model'] = self.ng_model
        if hasattr(self, 'ng_change'):
            kwargs['ng-change'] = self.ng_change + '()'
        kwargs['pickadate'] = "on"
        kwargs['week-starts-on'] = "1"
        kwargs['format'] = "dd/mm/yyyy"
        kwargs['size'] = 10
        return super(PickaDateField, self).__call__(**kwargs)


class SocoForm(FlaskForm):
    def flash_errors(self):
        for field, errors in self.errors.items():
            for error in errors:
                flash(u"Error in the %s field - %s" % (getattr(self, field).label.text, error))


class NcollForm(SocoForm):
    objname = 'evenement'
    titre = StringField('Titre', validators=[DataRequired(), Length(min=3, max=300)])
    sstitre = StringField('Sous-titre')
    date = PickaDateField('Date', objname=objname, format='%d/%m/%Y', validators=[DataRequired()])
    date_fin = PickaDateField('Date de fin', objname=objname, format='%d/%m/%Y', description="cas où l'événement dure plusieurs jours")
    lieu = StringField('Lieu', description="si laissé vide : %s" % app.config['SALLE_PPALE'])
    date_ouverture_inscriptions = PickaDateField("Date d'ouverture des inscriptions", objname=objname, 
                                                 format='%d/%m/%Y', validators=[DataRequired()])
    date_cloture_inscriptions = PickaDateField("Date de clôture des inscriptions", objname=objname, 
                                               format='%d/%m/%Y', validators=[DataRequired()])
    jour_par_jour = BooleanField('Voulez-vous que l\'inscription se fasse jour par jour&nbsp;?')
    champ_restauration_1 = BooleanField("Organisez-vous un repas/cocktail auquel vous voulez inviter les participants ? Si oui, cochez la case :")
    texte_restauration_1 = ClickStringField("et précisez alors la question que vous souhaitez leur poser sur votre page d'inscription",
                                            objname=objname, defaultvalue="Serez-vous des nôtres à midi ?",
                                                description="Exemple de question : 'Serez-vous des nôtres à midi ?'")
    champ_libre_1 = BooleanField("Souhaitez-vous poser une question supplémentaire aux participant-e-s ? Si oui, cochez la case :")
    texte_libre_1 = StringField("et précisez le texte de la question :")

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
    jours_de_presence =  [] #StringField('Jours de présence', validators=[DataRequired()],
    type_inscription = RadioField('Type d\'inscription', choices=[("presence","Vous assisterez au colloque"), ("interet","Vous n'assisterez pas au colloque, mais souhaitez établir un contact pour recevoir de l'information sur le sujet")])
    inscription_repas_1 = BooleanField('Repas 1')
    inscription_repas_2 = BooleanField('Repas 2')
    reponse_question_1 = StringField('Libre1')
    reponse_question_2 = StringField('Libre2')

    def __init__(self, formulaire, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.formulaire = formulaire
        if not formulaire.champ_attestation:
            self.__delitem__('attestation_demandee')
        if formulaire.jour_par_jour:
            if formulaire.evenement.date_fin == formulaire.evenement.date:
                self.__delitem__('jours_de_presence')
            else:
                for j in formulaire.evenement.calcule_jours():
                    jours_de_presence.append(BooleanField(j))
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
        if formulaire.champ_libre_1:
            self.__getitem__('reponse_question_1').label = Label('reponse_question_1', formulaire.texte_libre_1)
        else:
            self.__delitem__('reponse_question_1')
        if formulaire.champ_libre_2:
            self.__getitem__('reponse_question_2').label = Label('reponse_question_1', formulaire.texte_libre_2)
        else:
            self.__delitem__('reponse_question_2')

    def validate(self):
        if not FlaskForm.validate(self):
            self.flash_errors()
            return False
        return True
