from sqlalchemy import Table, Column, Integer, String, Text, DateTime, Date, Boolean, ForeignKey, Binary, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_restful import Resource, Api, reqparse
from flcoll import Base, api
from .texenv import escape_tex, TPL_ETIQUETTE


personne_organisation = Table('personne_organisation', Base.metadata,
                                  Column('id_personne', Integer, ForeignKey('personne.id')),
                                  Column('id_organisation', Integer, ForeignKey('organisation.id'))
                                  )
class Personne(Base):
    __tablename__ = 'personne'
    __table_args__ = (UniqueConstraint('nom', 'prenom', 'email', name='uc_pers'),)
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
    __table_args__ = (UniqueConstraint('uid_organisateur', 'date', 'titre', name='uc_even'),)
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

    def __init__(self, **kwargs):
        Base.__init__(self)
        for attrname in ['titre', 'sstitre', 'date', 'date_fin', 'lieu', 'resume', 'gratuite',
                             'uid_organisateur', 'id_entite_organisatrice']:
            if attrname in kwargs.keys():
                setattr(self, attrname, kwargs[attrname])

    def __repr__(self):
        return "%s (%s)" % (self.titre, self.date)

Organisation.evenement = relationship("Evenement", order_by=Evenement.date, back_populates="entite_organisatrice")


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
    champ_restauration_1 = Column(Boolean)
    texte_restauration_1 = Column(String(200))
    champ_restauration_2 = Column(Boolean)
    texte_restauration_2 = Column(String(200))
    upd = Column(DateTime, default=func.now(), server_default=func.now())

    evenement = relationship("Evenement", back_populates="formulaire")

    def __init__(self, **kwargs):
        Base.__init__(self)
        for attrname in ['id_evenement', 'evenement', 'date_ouverture_inscriptions', 'date_cloture_inscriptions',
                             'organisateur_en_copie', 'champ_attestation', 'champ_type_inscription',
                             'champ_restauration_1', 'texte_restauration_1', 'champ_restauration_2', 'texte_restauration_2']:
            if attrname in kwargs.keys():
                setattr(self, attrname, kwargs[attrname])

    def __str__(self):
        return "%s, %s (clôt. le %s)" % (self.evenement.titre, self.evenement.date, self.date_cloture_inscriptions)


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
        return "%s %s" % (self.personne.prenom, self.personne.nom)

    def genere_etiquette(self, base_x, base_y):
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
