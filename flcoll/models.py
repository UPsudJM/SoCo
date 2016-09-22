from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Binary, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flcoll import Base


class Evenement(Base):
    __tablename__ = 'evenement'
    id = Column(Integer, primary_key = True)
    logo = Column(Binary)
    titre = Column(String(200))
    sstitre = Column(String(200))
    date_debut = Column(DateTime)
    date_fin = Column(DateTime)
    lieu = Column(String(200))
    resume = Column(Text)
    uid_organisateur = Column(String(100))
    gratuite = Column(Boolean, default=True)
    upd = Column(DateTime)

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
    date_ouverture_inscriptions = Column(DateTime, nullable=False)
    date_cloture_inscriptions = Column(DateTime, nullable=False)
    organisateur_en_copie = Column(Boolean)
    champ_attestation = Column(Boolean)
    champ_type_inscription = Column(Boolean)
    champ_restauration_1 = Column(Boolean)
    texte_restauration_1 = Column(String(200))
    champ_restauration_2 = Column(Boolean)
    texte_restauration_2 = Column(String(200))
    upd = Column(DateTime)

    evenement = relationship("Evenement", back_populates="formulaire")

Evenement.formulaire = relationship("Formulaire", order_by=Formulaire.id, back_populates="evenement")


class Personne(Base):
    __tablename__ = 'personne'
    __table_args__ = (UniqueConstraint('nom', 'prenom', 'organisation', name='uc_1'),
                          UniqueConstraint('nom', 'prenom', 'email', name='uc_2'))
    id = Column(Integer, primary_key = True)
    nom = Column(String(70), nullable=False)
    prenom = Column(String(70))
    email = Column(String(70))
    telephone = Column(String(20))
    organisation = Column(String(70))
    fonction = Column(String(70))

    def __init__(self, **kwargs):
        Base.__init__(self)
        for attrname in ['nom', 'prenom', 'email', 'telephone', 'organisation', 'fonction']:
            if kwargs[attrname]:
                setattr(self, attrname, kwargs[attrname])

    def __str__(self):
        return "%s %s, %s (%s)" % (self.prenom, self.nom, self.organisation, self.fonction)


class Inscription(Base):
    __tablename__ = 'inscription'
    __table_args__ = (UniqueConstraint('id_evenement', 'id_personne', name='uc_3'),)
    id = Column(Integer, primary_key = True)
    id_evenement = Column(Integer, ForeignKey('evenement.id'), nullable=False)
    id_personne = Column(Integer, ForeignKey('personne.id'), nullable=False)
    date_inscription = Column(DateTime, default=func.now(), server_default=func.now())
    type_inscription = Column(String(70))
    attestation_demandee = Column(Boolean)
    commentaire = Column(String(200))
    inscription_repas_1 = Column(Boolean)
    inscription_repas_2 = Column(Boolean)

    evenement = relationship("Evenement", back_populates="inscriptions")
    personne = relationship("Personne", back_populates="inscriptions")

    def __init__(self, evenement, personne):
        Base.__init__(self)
        self.evenement = evenement
        self.personne = personne

    def __str__(self):
        return "%s %s, le %s" % (self.personne.prenom, self.personne.nom, self.date_inscription)

Evenement.inscriptions = relationship("Inscription", order_by=Inscription.id, back_populates="evenement")
Personne.inscriptions = relationship("Inscription", order_by=Inscription.id, back_populates="personne")
