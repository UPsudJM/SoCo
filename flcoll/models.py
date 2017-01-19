from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, ForeignKey, Binary, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_restful import Resource, Api, reqparse
from flcoll import Base, api


class Evenement(Base):
    __tablename__ = 'evenement'
    id = Column(Integer, primary_key = True)
    logo = Column(Binary)
    titre = Column(String(200))
    sstitre = Column(String(200))
    date = Column(Date)
    date_fin = Column(Date)
    lieu = Column(String(400)) #, default="Faculté Jean Monnet, Salle Vedel, Université Paris Sud/Paris-Saclay")
    resume = Column(Text)
    uid_organisateur = Column(String(100))
    gratuite = Column(Boolean, default=True)
    upd = Column(DateTime, default=func.now(), server_default=func.now())

    def __init__(self, titre=None, date_debut=None, uid_organisateur=None):
        self.titre = titre
        self.date_debut = date_debut
        self.uid_organisateur = uid_organisateur

    def __repr__(self):
        return "%s (%s)" % (self.titre, self.uid_organisateur)


class Formulaire(Base):
    __tablename__ = 'formulaire'
    id = Column(Integer, primary_key = True)
    id_evenement = Column(Integer, ForeignKey('evenement.id'), nullable=False)
    date_ouverture_inscriptions = Column(Date, nullable=False)
    date_cloture_inscriptions = Column(Date, nullable=False)
    organisateur_en_copie = Column(Boolean)
    champ_attestation = Column(Boolean, default=True)
    champ_type_inscription = Column(Boolean)
    champ_restauration_1 = Column(Boolean)
    texte_restauration_1 = Column(String(200))
    champ_restauration_2 = Column(Boolean)
    texte_restauration_2 = Column(String(200))
    upd = Column(DateTime, default=func.now(), server_default=func.now())

    evenement = relationship("Evenement", back_populates="formulaire")

Evenement.formulaire = relationship("Formulaire", order_by=Formulaire.id, back_populates="evenement")


class Personne(Base):
    __tablename__ = 'personne'
    __table_args__ = (UniqueConstraint('nom', 'prenom', 'email', name='uc_1'),)
    id = Column(Integer, primary_key = True)
    nom = Column(String(70), nullable=False)
    prenom = Column(String(70))
    email = Column(String(70))

    def __init__(self, **kwargs):
        Base.__init__(self)
        for attrname in ['nom', 'prenom', 'email']:
            if attrname in kwargs.keys():
                setattr(self, attrname, kwargs[attrname])

    def __str__(self):
        return "%s %s, %s (%s)" % (self.prenom, self.nom, self.organisation, self.fonction)


class Inscription(Base):
    __tablename__ = 'inscription'
    __table_args__ = (UniqueConstraint('id_evenement', 'id_personne', name='uc_2'),)
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
    commentaire = Column(String(200))
    inscription_repas_1 = Column(Boolean)
    inscription_repas_2 = Column(Boolean)

    evenement = relationship("Evenement", back_populates="inscription")
    personne = relationship("Personne", back_populates="inscription")

    def __init__(self, **kwargs):
        Base.__init__(self)
        for attrname in ['id_evenement', 'evenement', 'id_personne', 'personne', 'telephone', 'fonction', 'organisation',
                             'date_inscription', 'badge1', 'badge2', 'type_inscription', 'attestation_demandee',
                             'commentaire', 'inscription_repas_1', 'inscription_repas_2']:
            if attrname in kwargs.keys():
                setattr(self, attrname, kwargs[attrname])

    def __str__(self):
        return "%s %s, le %s" % (self.personne.prenom, self.personne.nom, self.date_inscription)

Evenement.inscription = relationship("Inscription", order_by=Inscription.id, back_populates="evenement")
Personne.inscription = relationship("Inscription", order_by=Inscription.id, back_populates="personne")

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
