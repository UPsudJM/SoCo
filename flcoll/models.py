from sqlalchemy import Table, Column, Integer, String, Text, DateTime, Date, Boolean, ForeignKey, Binary, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config import LOGO_DEFAULT
from flcoll import Base, apiman


personne_organisation = Table('personne_organisation', Base.metadata,
                                  Column('id_personne', Integer, ForeignKey('personne.id')),
                                  Column('id_organisation', Integer, ForeignKey('organisation.id'))
                                  )
class Personne(Base):
    __tablename__ = 'personne'
    __table_args__ = (UniqueConstraint('nom', 'prenom', 'email', name='uc_1'),)
    id = Column(Integer, primary_key = True)
    nom = Column(String(70), nullable=False)
    prenom = Column(String(70))
    email = Column(String(70))
    organisations = relationship("Organisation", secondary=personne_organisation)

    def __init__(self, **kwargs):
        Base.__init__(self)
        for attrname in ['nom', 'prenom', 'email']:
            if attrname in kwargs.keys():
                setattr(self, attrname, kwargs[attrname])

    def __str__(self):
        return "%s %s" % (self.prenom, self.nom)


class Organisation(Base):
    __tablename__ = 'organisation'
    __table_args__ = (UniqueConstraint('nom', name='uc_1'),)
    id = Column(Integer, primary_key = True)
    nom = Column(String(70), nullable=False)
    interne = Column(Boolean, default=False)
    email = Column(String(70))
    logo = Column(String(200))
    personnes = relationship("Personne", secondary=personne_organisation)

    def __init__(self, **kwargs):
        Base.__init__(self)
        for attrname in ['nom', 'interne', 'email']:
            if attrname in kwargs.keys():
                setattr(self, attrname, kwargs[attrname])

    def __str__(self):
        return self.nom


class Evenement(Base):
    __tablename__ = 'evenement'
    id = Column(Integer, primary_key = True)
    titre = Column(String(200))
    sstitre = Column(String(200))
    date = Column(Date)
    date_fin = Column(Date)
    lieu = Column(String(400)) #, default="Faculté Jean Monnet, Salle Vedel, Université Paris Sud/Paris-Saclay")
    resume = Column(Text)
    gratuite = Column(Boolean, default=True)
    uid_organisateur = Column(String(100))
    id_entite_organisatrice = Column(Integer, ForeignKey('organisation.id'), nullable=True)
    logo = Column(String(200))
    upd = Column(DateTime, default=func.now(), server_default=func.now())
    #upd = Column(DateTime)

    entite_organisatrice = relationship("Organisation", back_populates="evenement")

    def __init__(self, titre=None, date_debut=None, uid_organisateur=None):
        self.titre = titre
        self.date_debut = date_debut
        self.uid_organisateur = uid_organisateur

    def __repr__(self):
        return "%s (%s)" % (self.titre, self.date)

Organisation.evenement = relationship("Evenement", order_by=Evenement.date, back_populates="entite_organisatrice")


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

    def __str__(self):
        return "%s %s" % (self.personne.prenom, self.personne.nom)

Evenement.inscription = relationship("Inscription", order_by=Inscription.id, back_populates="evenement")
Personne.inscription = relationship("Inscription", order_by=Inscription.id, back_populates="personne")

# pour URLs http://127.0.0.1:5000/api/inscription et http://127.0.0.1:5000/api/inscription/%d
# et aussi http://127.0.0.1:5000/api/evenement/%d/inscription etc...
api_evenement = apiman.create_api(Evenement, methods = ['GET', 'POST'])
api_inscription = apiman.create_api(Inscription, methods = ['GET', 'POST'])
