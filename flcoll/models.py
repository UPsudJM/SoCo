from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from flcoll import Base


class Evenement(Base):
    __tablename__ = 'evenement'
    id = Column(Integer, primary_key = True)
    titre = Column(String(200))
    sstitre = Column(String(200))
    date_debut = Column(DateTime)
    date_fin = Column(DateTime)
    lieu = Column(String(200))
    resume = Column(Text)
    uid_organisateur = Column(String(100))
    gratuite = Column(Boolean)
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
    evenement = Column(ForeignKey('evenement.id'))
    date_ouverture_inscriptions = Column(DateTime)
    date_cloture_inscriptions = Column(DateTime)
    upd = Column(DateTime)
    organisateur_en_copie = Column(Boolean)
    champ_attestation = Column(Boolean)
    champ_type_inscription = Column(Boolean)
    champ_restauration_1 = Column(Boolean)
    texte_restauration_1 = Column(String(200))
    champ_restauration_1 = Column(Boolean)
    texte_restauration_2 = Column(String(200))


class Personne(Base):
    __tablename__ = 'personne'
    id = Column(Integer, primary_key = True)
    nom = Column(String(70))
    prenom = Column(String(70))
    email = Column(String(70))
    telephone = Column(String(20))
    organisation = Column(String(70))
    fonction = Column(String(70))

    def __str__(self):
        return "%s %s, %s (%s)" % (self.prenom, self.nom, self.organisation, self.fonction)


class Inscription(Base):
    __tablename__ = 'inscription'
    id = Column(Integer, primary_key = True)
    evenement = Column(ForeignKey('evenement.id'))
    personne = Column(ForeignKey('personne.id'))
    date_inscription = Column(DateTime)
    type_inscription = Column(String(70))
    attestation_demandee = Column(Boolean)
    commentaire = Column(String(200))
    inscription_repas_1 = Column(Boolean)
    inscription_repas_2 = Column(Boolean)
    
    def __str__(self):
        return "%s %s, le %s" % (self.personne.prenom, self.personne.nom, self.date_inscription)

