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

import datetime, enum
from sqlalchemy import Table, Column, Integer, String, Text, DateTime, Date, Boolean, ForeignKey, Binary, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_restful import Resource, Api, reqparse
from soco import Base, api, db_session, LOGO_DEFAULT, URL_DEFAULT
from .texenv import escape_tex, TPL_ETIQUETTE, TPL_ETIQUETTE_DOUBLELOGO


personne_organisation = Table('personne_organisation', Base.metadata,
                                  Column('id_personne', Integer, ForeignKey('personne.id')),
                                  Column('id_organisation', Integer, ForeignKey('organisation.id'))
                                  )
lieu_organisation = Table('lieu_organisation', Base.metadata,
                                  Column('id_lieu', Integer, ForeignKey('lieu.id')),
                                  Column('id_organisation', Integer, ForeignKey('organisation.id'))
                                  )

class Personne(Base):
    __tablename__ = 'personne'
    __table_args__ = (UniqueConstraint('nom', 'prenom', 'email', name='uc_pers'), UniqueConstraint('token', name='uc_tok'),)
    id = Column(Integer, primary_key = True)
    nom = Column(String(70), nullable=False)
    prenom = Column(String(70))
    email = Column(String(70))
    token = Column(String(200))
    organisations = relationship("Organisation", secondary=personne_organisation)

    def __init__(self, **kwargs):
        Base.__init__(self)
        for attrname in ['nom', 'prenom', 'email']:
            if attrname in kwargs.keys():
                setattr(self, attrname, kwargs[attrname])

    def __str__(self):
        return "%s %s" % (self.prenom, self.nom)

    @classmethod
    def chkemail(self, evt, email_a_verifier, nom_a_verifier, prenom_a_verifier):
        p_trouvees = self.query.filter_by(email=email_a_verifier).all()
        if not p_trouvees:
            return [-1, "non"]
        id_personne = 0
        for p in p_trouvees:
            if p.nom.lower() == nom_a_verifier.lower() and p.prenom.lower() == prenom_a_verifier.lower():
                id_personne = p.id
                for i in p.inscription:
                    print(i.id_evenement)
                    if i.id_evenement == int(evt):
                        return [id_personne, "oui"]
        return [id_personne, "non"]


class Organisation(Base):
    __tablename__ = 'organisation'
    __table_args__ = (UniqueConstraint('nom', name='uc_orga'),)
    id = Column(Integer, primary_key = True)
    nom = Column(String(70), nullable=False)
    interne = Column(Boolean, default=False)
    email = Column(String(70))
    logo = Column(String(200))
    url = Column(String(200))
    personnes = relationship("Personne", secondary=personne_organisation)
    lieux = relationship("Lieu", secondary=lieu_organisation)

    def __init__(self, **kwargs):
        Base.__init__(self)
        for attrname in ['nom', 'interne', 'email']:
            if attrname in kwargs.keys():
                setattr(self, attrname, kwargs[attrname])

    def __str__(self):
        return self.nom


class Lieu(Base):
    __tablename__ = 'lieu'
    __table_args__ = (UniqueConstraint('nom', 'adresse', name='uc_lieu'),)
    id = Column(Integer, primary_key = True)
    nom = Column(String(20))
    adresse = Column(String(200))
    capacite = Column(Integer)

    def __init__(self, **kwargs):
        Base.__init__(self)
        for attrname in ['nom', 'adresse', 'capacite']:
            if attrname in kwargs.keys():
                setattr(self, attrname, kwargs[attrname])

    def __str__(self):
        return self.nom


class RecurrenceEnum(enum.Enum):
    quotidien = "quotidien"
    hebdomadaire = "hebdomadaire"
    mensuel = "mensuel"
    annuel = "annuel"


class Evenement(Base):
    __tablename__ = 'evenement'
    __table_args__ = (UniqueConstraint('uid_organisateur', 'date', 'titre', name='uc_even'),)
    id = Column(Integer, primary_key = True)
    titre = Column(String(200))
    sstitre = Column(String(200))
    date = Column(Date)
    date_fin = Column(Date)
    id_lieu = Column(Integer, ForeignKey('lieu.id'), nullable=True)
    recurrence = Column('recurrence', Enum(RecurrenceEnum))
    resume = Column(Text)
    gratuite = Column(Boolean, default=True)
    uid_organisateur = Column(String(100))
    id_entite_organisatrice = Column(Integer, ForeignKey('organisation.id'), nullable=True)
    logo = Column(String(200))
    url = Column(String(200))
    upd = Column(DateTime, default=func.now(), server_default=func.now())
    #upd = Column(DateTime)

    entite_organisatrice = relationship("Organisation", back_populates="evenement")
    lieu = relationship("Lieu", back_populates="evenement")

    def __init__(self, **kwargs):
        Base.__init__(self)
        for attrname in ['titre', 'sstitre', 'date', 'date_fin', 'lieu', 'resume', 'gratuite',
                             'uid_organisateur', 'id_entite_organisatrice']:
            if attrname in kwargs.keys():
                setattr(self, attrname, kwargs[attrname])

    def __repr__(self):
        return "%s (%s)" % (self.titre, self.date)

    @classmethod
    def modif_attributs(self, evt, **kwargs):
        e = self.query.get(evt)
        for a in ['titre', 'sstitre', 'lieu']:
            if kwargs.has_key(a) and kwargs[a]:
                setattr(e, a, kwargs[a])
        db_session.add(e)
        try:
            db_session.commit()
        except:
            raise IntegrityError("Unknown error")

    def infos_comm(self):
        """Calcule et retourne 2 logos et une URL"""
        logo0, url0 = LOGO_DEFAULT, URL_DEFAULT
        logo = evenement.logo
        url = self.url or ""
        if not logo or not url:
            organisation = self.entite_organisatrice
            if organisation:
                if not logo and organisation.logo:
                    logo = organisation.logo
                if not url and organisation.url:
                    url = organisation.url
        if not url and url0:
            url = url0
        return logo0, logo, url

    def calcule_jours(self):
        """ Retourne une liste des jours de colloque"""
        d = self.date
        delta = self.date_fin - self.date
        ret = [d]
        for i in range(delta.days):
            ret.append(d + i + 1)
        return ret

    def calcule_nuits(self):
        """ Retourne une liste des nuits"""
        d = self.date
        delta = self.date_fin - self.date
        ret = [d]
        for i in range(delta.days):
            ret.append(d + i + 1)
        return ret

    def calcule_repas(self):
        """ Retourne une liste des repas"""
        d = self.date
        delta = self.date_fin - self.date
        ret = [d]
        for i in range(delta.days):
            ret.append(d + i + 1)
        return ret

Organisation.evenement = relationship("Evenement", order_by=Evenement.date, back_populates="entite_organisatrice")
Lieu.evenement = relationship("Evenement", order_by=Evenement.date, back_populates="lieu")


class Formulaire(Base):
    __tablename__ = 'formulaire'
    __table_args__ = (UniqueConstraint('id_evenement', 'date_ouverture_inscriptions', name='uc_form'),)
    id = Column(Integer, primary_key = True)
    id_evenement = Column(Integer, ForeignKey('evenement.id'), nullable=False)
    date_ouverture_inscriptions = Column(Date, nullable=False)
    date_cloture_inscriptions = Column(Date, nullable=False)
    organisateur_en_copie = Column(Boolean)
    champ_attestation = Column(Boolean, default=True)
    champ_type_inscription = Column(Boolean)
    jour_par_jour = Column(Boolean)
    champ_restauration_1 = Column(Boolean)
    texte_restauration_1 = Column(String(200))
    champ_restauration_2 = Column(Boolean)
    texte_restauration_2 = Column(String(200))
    champ_libre_1 = Column(Boolean)
    texte_libre_1 = Column(String(200))
    champ_libre_2 = Column(Boolean)
    texte_libre_2 = Column(String(200))
    formulaire_intervenant = Column(Boolean)
    upd = Column(DateTime, default=func.now(), server_default=func.now())

    evenement = relationship("Evenement", back_populates="formulaire")

    def __init__(self, **kwargs):
        Base.__init__(self)
        for attrname in ['id_evenement', 'evenement', 'date_ouverture_inscriptions', 'date_cloture_inscriptions',
                             'organisateur_en_copie', 'champ_attestation', 'champ_type_inscription',
                             'champ_restauration_1', 'texte_restauration_1', 'champ_restauration_2', 'texte_restauration_2',
                             'champ_libre_1', 'texte_libre_1', 'champ_libre_2', 'texte_libre_2',]:
            if attrname in kwargs.keys():
                setattr(self, attrname, kwargs[attrname])

    def __str__(self):
        return "%s, %s (clôt. le %s)" % (self.evenement.titre, self.evenement.date, self.date_cloture_inscriptions)

    @classmethod
    def modif_date_cloture(self, form, date):
        f = self.query.get(form)
        f.date_cloture_inscriptions = date
        db_session.add(f)
        try:
            db_session.commit()
        except:
            raise IntegrityError("Unknown error")

    @classmethod
    def get_uid_organisateur(self, form):
        f = self.query.get(form)
        return f.evenement.uid_organisateur


Evenement.formulaire = relationship("Formulaire", order_by=Formulaire.id, back_populates="evenement")


class Inscription(Base):
    __tablename__ = 'inscription'
    __table_args__ = (UniqueConstraint('id_evenement', 'id_personne', name='uc_insc'),)
    id = Column(Integer, primary_key = True)
    id_evenement = Column(Integer, ForeignKey('evenement.id'), nullable=False)
    id_personne = Column(Integer, ForeignKey('personne.id'), nullable=False)
    date_inscription = Column(DateTime) #, default=func.now(), server_default=func.now())
    type_inscription = Column(String(70))
    telephone = Column(String(20))
    organisation = Column(String(70))
    fonction = Column(String(70))
    badge1 = Column(String(70))
    badge2 = Column(String(70))
    attestation_demandee = Column(Boolean)
    jours_de_presence = Column(String(20))
    commentaire = Column(String(200))
    inscription_repas_1 = Column(Boolean)
    inscription_repas_2 = Column(Boolean)

    evenement = relationship("Evenement", back_populates="inscription")
    personne = relationship("Personne", back_populates="inscription")

    def __init__(self, **kwargs):
        Base.__init__(self)
        for attrname in ['id_evenement', 'evenement', 'id_personne', 'personne', 'telephone', 'fonction', 'organisation',
                             'date_inscription', 'badge1', 'badge2', 'type_inscription', 'attestation_demandee',
                             'jours_de_presence', 'commentaire', 'inscription_repas_1', 'inscription_repas_2']:
            if attrname in kwargs.keys():
                setattr(self, attrname, kwargs[attrname])

    def __str__(self):
        return "%s %s" % (self.personne.prenom, self.personne.nom)

    def genere_etiquette(self, base_x, base_y):
        if self.evenement.logo:
            return self.genere_etiquette_doublelogo(base_x, base_y)
        if len(self.badge1) < 22:
            police1 = "\\normalsize"
        else:
            police1 = "\\small"
        if len(self.badge2) < 30:
            police2 = "\\normalsize"
        else:
            police2 = "\\small"
        return TPL_ETIQUETTE % (base_x - 10, base_y + 50,
                                    base_x, base_y, police1, escape_tex(self.badge1), police2, escape_tex(self.badge2))

    def genere_etiquette_doublelogo(self, base_x, base_y, logo=None):
        if not logo:
            logo = self.evenement.logo
            if not logo:
                return self.genere_etiquette(base_x, base_y)
        if len(self.badge1) < 22:
            police1 = "\\normalsize"
        else:
            police1 = "\\small"
        if len(self.badge2) < 30:
            police2 = "\\normalsize"
        else:
            police2 = "\\small"
        return TPL_ETIQUETTE_DOUBLELOGO % (base_x - 10, base_y + 50,
                                    base_x, base_y, logo, police1, escape_tex(self.badge1), police2, escape_tex(self.badge2))

Evenement.inscription = relationship("Inscription", order_by=Inscription.id, back_populates="evenement")
Personne.inscription = relationship("Inscription", order_by=Inscription.id, back_populates="personne")


class MaterielEnum(enum.Enum):
    ordinateur = "ordi"
    videoprojvga = "videoprojVGA"
    videoprojhdmi = "videoprojHDMI"
    internet = "internet"


class TransportEnum(enum.Enum):
    avion = "avion"
    train = "train"
    autocar = "autocar"
    voiture = "voiture"
    covoiturage = "covoiturage"


class Intervenant(Base):
    __tablename__ = 'intervenant'
    __table_args__ = (UniqueConstraint('id_inscription', name='uc_intv'),)
    id = Column(Integer, primary_key = True)
    id_inscription = Column(Integer, ForeignKey('inscription.id'), nullable=False)
    besoin_materiel = Column('besoin_materiel', Enum(MaterielEnum))
    transport_aller = Column('transport_aller', Enum(TransportEnum))
    ville_depart_aller = Column(String(200)) # ville ou aéroport
    horaire_depart_aller = Column(DateTime)
    transport_retour = Column('transport_retour', Enum(TransportEnum))
    ville_arrivee_retour = Column(String(200))
    horaire_depart_retour = Column(DateTime)
    nuits = Column(String(20))
    repas = Column(String(20))

    inscription = relationship("Inscription", back_populates="intervenant")


    def __init__(self, **kwargs):
        Base.__init__(self)
        for attrname in ['id_inscription', 'inscription', 'besoin_materiel', 'transport_aller', 'ville_depart_aller',
                             'horaire_depart_aller', 'transport_retour', 'ville_arrivee_retour', 'horaire_depart_retour',
                             'nuits', 'repas']:
            if attrname in kwargs.keys():
                setattr(self, attrname, kwargs[attrname])

    def __str__(self):
        return "%s %s (%s)" % (self.inscription.personne.prenom, self.inscription.personne.nom, self.ville_depart_aller)

Inscription.intervenant = relationship("Intervenant", order_by=Inscription.id, back_populates="inscription")


# API RESTful
@api.resource('/api/chkemail/')
class ChkEmail(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('evt', required=True, help="Evenement cannot be blank!")
        parser.add_argument('email', required=True, help="Email cannot be blank!")
        parser.add_argument('nom', required=True, help="Nom cannot be blank!")
        parser.add_argument('prenom', required=True, help="Prenom cannot be blank!")
        args = parser.parse_args()
        try:
            evt = int(args['evt'])
        except:
            raise ValueError("'%s' is not a valid event id" % args['evt'])
        return Personne.chkemail(evt, args['email'], args['nom'], args['prenom'])

@api.resource('/api/envoicodeverif/')
class CodeVerif(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help="Email cannot be blank!")
        args = parser.parse_args()
        from .emails import envoyer_code_verification
        codeverif = envoyer_code_verification(args['email'])
        return codeverif

@api.resource('/api/modifformulaire/')
class ModifFormulaire(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, help="Le formulaire à modifier doit être spécifié")
        parser.add_argument('datecloture', required=True, help="Date de clôture à modifier ?")
        args = parser.parse_args()
        from .emails import envoyer_mail_modification_formulaire
        try:
            id_formulaire = int(args['id'])
        except:
            raise ValueError("'%s' is not a valid form id" % args['id'])
        try:
            date_cloture = datetime.datetime.strptime(args['datecloture'], '%Y-%m-%d').strftime('%Y-%m-%d')
        except:
            raise ValueError("'%s' is not a valid date" % args['datecloture'])
        f = Formulaire.query.get(id_formulaire)
        if str(f.date_cloture_inscriptions) == date_cloture:
            return
        f.date_cloture_inscriptions = date_cloture
        db_session.add(f)
        try:
            db_session.commit()
        except:
            raise IntegrityError("Unknown error")
        uid_organisateur = f.evenement.uid_organisateur
        envoyer_mail_modification_formulaire(uid_organisateur,
                                                 f.evenement,
                                                 date_cloture_inscriptions = f.date_cloture_inscriptions.strftime('%d/%m/%Y'))
        return f.date_cloture_inscriptions.strftime("%d/%m/%Y")

@api.resource('/api/modifevenement/')
class ModifEvenement(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, help="L'événement à modifier doit être spécifié")
        parser.add_argument('titre', required=False, help="Titre à modifier ?")
        parser.add_argument('sstitre', required=False, help="Sous-titre à modifier ?")
        parser.add_argument('lieu', required=False, help="Lieu à modifier ?")
        args = parser.parse_args()
        try:
            id_evenement = int(args['id'])
        except:
            raise ValueError("'%s' is not a valid form id" % args['id'])
        from .emails import envoyer_mail_modification_formulaire
        Evenement.modif_attributs(id_evenement, args)
        uid_organisateur = Evenement.get_uid_organisateur(id_evenement)
        envoyer_mail_modification_formulaire(uid_organisateur, **kwargs)
