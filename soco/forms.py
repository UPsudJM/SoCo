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

from flask_wtf import FlaskForm
from flask import flash
from flask_babelex import gettext
from wtforms import StringField, BooleanField, RadioField, DateField, DateTimeField, SelectField, SelectMultipleField, HiddenField, FieldList, FormField
from wtforms.fields import Label
from wtforms.validators import DataRequired, Optional, Length, Email
from soco.models import Evenement, Formulaire, Personne, Inscription, Lieu, Intervenant
from soco.auth.models import User
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
        objname, name = None, None
        if 'objname' in kwargs.keys():
            objname = kwargs['objname']
            del kwargs['objname']
        if '_name' in kwargs.keys():
            name = kwargs['_name'].replace("-", ".") # pour le sous-formulaire
        changefunc = None
        if 'changefunc' in kwargs.keys():
            changefunc = args['changefunc']
            del args['changefunc']
        super(PickaDateField, self).__init__(*args, **kwargs)
        if objname and name:
            self.ng_model = objname + '.' + name
        elif name:
            self.ng_model = name
        else:
            self.ng_model = None
        if changefunc:
            self.ng_change = changefunc
        elif self.name:
            self.ng_change = "calc_" + self.name.replace("evenement-", "")
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


class EvenementForm(SocoForm):
    objname = 'evenement'
    organisateurs = SelectMultipleField(gettext('Organisé par'), coerce=int, choices = [],
                                            description = gettext("Plusieurs choix possibles"))
    titre = StringField(gettext('Titre'), validators=[DataRequired(), Length(min=3, max=300)])
    sstitre = StringField(gettext('Sous-titre'))
    date = PickaDateField(gettext('Date'), objname=objname, format='%d/%m/%Y', validators=[DataRequired()])
    date_fin = PickaDateField(gettext('Date de fin'), objname=objname, format='%d/%m/%Y',
                                  description = gettext("Seulement dans le cas où l'événement dure plusieurs jours"))
    if app.config['AVEC_RECURRENCE']:
        recurrence = RadioField(gettext('Récurrence :'), default = '', choices = list(Evenement.RECURRENCE.items()))
    else:
        recurrence = HiddenField(gettext('Récurrence'))
    lieu = SelectField(
        gettext('Lieu'), coerce=int, choices = [],
        description=gettext('Choisissez la salle, ou le lieu, dans la liste. S\'il ne figure pas, laissez vide'))

    def __init__(self, **kwargs):
        SocoForm.__init__(self, **kwargs)
        self.organisateurs.choices = [ (u.id, u.get_gecos()) for u in User.query.filter(User.role!='superadmin').order_by(User.username).all() ]
        self.lieu.choices = [ (0, ' -- ') ] + [ (l.id, l.nom) for l in Lieu.query.order_by(Lieu.nom).all() ]


class FormulaireForm(SocoForm):
    objname = 'formulaire'
    evenement = FormField(EvenementForm)
    date_ouverture_inscriptions = PickaDateField(gettext("Date d'ouverture des inscriptions"), objname=objname,
                                                 format='%d/%m/%Y', validators=[DataRequired()])
    date_cloture_inscriptions = PickaDateField(gettext("Date de clôture des inscriptions"), objname=objname,
                                               format='%d/%m/%Y', validators=[DataRequired()])
    jour_par_jour = BooleanField(gettext('Voulez-vous que l\'inscription se fasse jour par jour&nbsp;?'))
    champ_restauration_1 = BooleanField(
        gettext("Organisez-vous un repas/cocktail auquel vous voulez inviter les participants, ou encore, avez-vous une autre question à leur poser ? Si oui, cochez la case :"),
        description=gettext("Vous pouvez aussi vouloir poser une autre question, le texte est à votre discrétion")
        )
    texte_restauration_1 = ClickStringField(
        gettext("et précisez alors la question que vous souhaitez leur poser sur votre page d'inscription"),
        objname=objname, defaultvalue=gettext("Serez-vous des nôtres à midi ?"),
        description=gettext("Le texte de votre question (avec réponse par oui ou par non)"),
        clickfunc=""
        )
    champ_libre_1 = BooleanField(
        gettext("Souhaitez-vous poser une question supplémentaire aux participant-e-s ? Si oui, cochez la case :"))
    texte_libre_1 = StringField(gettext("et précisez le texte de la question :"))

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.date_ouverture_inscriptions.data > self.date_cloture_inscriptions.data:
            self.date_ouverture_inscriptions.errors.append(
                gettext("La date d'ouverture ne peut pas être antérieure à la date de clôture")
                )
            return False
        if (self.evenement.date_fin.data and self.date_cloture_inscriptions.data > self.evenement.date_fin.data) \
          or (not self.evenement.date_fin.data and self.date_cloture_inscriptions.data > self.evenement.date.data):
            self.date_ouverture_inscriptions.errors.append(
                gettext("La date de clôture ne peut pas être postérieure à la date de l'événement")
                )
            return False
        auj = datetime.date.today()
        if not self.date_ouverture_inscriptions.data or self.date_ouverture_inscriptions.data < auj:
            self.date_ouverture_inscriptions.data = auj
        return True


class InscriptionForm(SocoForm):
    nom = StringField(gettext('Nom'), validators=[DataRequired(), Length(min=2, max=30)], render_kw={'autocomplete':'family-name'})
    prenom = StringField(
        gettext('Prénom'),
        validators=[Optional(), Length(min=0, max=30)],
        description=gettext("Attention, pour le badge : prénom + nom = 26 caractères max."),
        render_kw={'autocomplete':'given-name'}
        )
    email = StringField(gettext('Adresse électronique'), validators=[DataRequired(), Email(), Length(min=0, max=70)],
                            render_kw={'autocomplete':'email'})
    telephone = StringField(gettext('Téléphone'), validators=[Optional(), Length(min=0, max=20)])
    organisation = StringField(
        gettext('Organisation'),
        validators=[DataRequired(), Length(min=0, max=40)],
        description=gettext("Attention, pour le badge : fonction + organisation = 32 caractères max."),
        render_kw={'autocomplete':'organization'}
        )
    fonction = StringField(gettext('Fonction'), validators=[Optional(), Length(min=0, max=40)])
    if app.config['AVEC_ETIQUETTES']:
        badge1 = StringField(gettext('Badge1'), validators=[DataRequired(), Length(min=1, max=27)], render_kw={'autocomplete':'off'})
        badge2 = StringField(gettext('Badge2'), validators=[DataRequired(), Length(min=1, max=33)], render_kw={'autocomplete':'off'})
    else:
        badge1 = StringField(gettext('Badge1'), validators=[], render_kw={'autocomplete':'off'})
        badge2 = StringField(gettext('Badge2'), validators=[], render_kw={'autocomplete':'off'})
    attestation_demandee = BooleanField(gettext('Cochez cette case si vous désirez une attestation de présence&nbsp;:'))
    jours_de_presence = FieldList(BooleanField('jour'), min_entries=0, max_entries=100)
    type_inscription = RadioField(
        'Type d\'inscription',
        choices=[
            ("presence", gettext("Vous assisterez à l'évenement")),
            ("interet", gettext("Vous n'assisterez pas à l'évenement, mais souhaitez établir un contact pour recevoir de l'information sur le sujet"))
            ])
    inscription_repas_1 = BooleanField(gettext('Repas 1'))
    inscription_repas_2 = BooleanField(gettext('Repas 2'))
    reponse_question_1 = StringField(gettext('Libre 1'))
    reponse_question_2 = StringField(gettext('Libre 2'))

    def __init__(self, formulaire, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.formulaire = formulaire
        if not formulaire.champ_attestation:
            self.__delitem__('attestation_demandee')
        if formulaire.jour_par_jour or formulaire.evenement.recurrence:
            if formulaire.evenement.date_fin == formulaire.evenement.date:
                self.__delitem__('jours_de_presence')
            else:
                formulaire.evenement.calcule_jours()
                for i in range(len(formulaire.evenement.jours)):
                    j = formulaire.evenement.jours[i]
                    self.jours_de_presence.append_entry()
                    self.jours_de_presence.entries[i].value = "jour-" + j.strftime("%x")
                    self.jours_de_presence.entries[i].label = j.strftime("%A %d %b")
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


class IntervenantForm(InscriptionForm):
    besoin_materiel = SelectField(gettext('Matériel à prévoir'),
                                      choices = Intervenant.MATERIEL.items(),
                                      description = gettext("Éventuellement, matériel que nous devons prévoir pour votre intervention"))
    transport_aller = SelectField(gettext('Moyen de transport (trajet aller)'),
                                      choices = Intervenant.TRANSPORT.items(),
                                      description = gettext("Devons-nous prévoir votre transport aller ?"))
    ville_depart_aller = StringField(gettext('Gare, aéroport, ou ville de départ (trajet aller)'))
    horaire_depart_aller = StringField(gettext('Horaire de départ (trajet aller)'))
    transport_retour = SelectField(gettext('Moyen de transport (trajet retour)'),
                                      choices = Intervenant.TRANSPORT.items(),
                                      description = gettext("Devons-nous prévoir votre transport retour ?"))
    ville_arrivee_retour = StringField(gettext('Gare, aéroport, ou ville de destination (trajet retour)'))
    horaire_depart_retour = StringField(gettext('Horaire de départ (trajet retour)'))
    nuits = FieldList(BooleanField('nuit'), min_entries=0, max_entries=10)
    repas = FieldList(BooleanField('repas'), min_entries=0, max_entries=20)

    def __init__(self, formulaire, *args, **kwargs):
        InscriptionForm.__init__(self, formulaire, *args, **kwargs)
        formulaire.evenement.calcule_jours()
        for i in range(len(formulaire.evenement.nuits)):
            n = formulaire.evenement.nuits[i]
            self.nuits.append_entry()
            self.nuits.entries[i].value = "nuit-" + n.strftime("%y-%m-%d")
            self.nuits.entries[i].label = gettext("nuit du") + ' {day} ({weekday} {soir})' . format(
                day=n.day, weekday=gettext(n.strftime("%A")), soir=gettext("soir"))
        for i in range(len(formulaire.evenement.jours)):
            j = formulaire.evenement.jours[i]
            self.repas.append_entry()
            self.repas.entries[2 * i].value = "midi-" + j.strftime("%y-%m-%d")
            self.repas.entries[2 * i].label = '{day} ' . format(day=j.day) + ' ' + gettext('midi')
            self.repas.append_entry()
            self.repas.entries[2 * i + 1].value = "soir-" + j.strftime("%y-%m-%d")
            self.repas.entries[2 * i + 1].label = '{day} ' . format(day=j.day) + ' ' + gettext('soir')
