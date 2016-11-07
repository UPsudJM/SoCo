from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
inscription = Table('inscription', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('id_evenement', Integer, nullable=False),
    Column('id_personne', Integer, nullable=False),
    Column('date_inscription', DateTime),
    Column('type_inscription', String(length=70)),
    Column('telephone', String(length=20)),
    Column('organisation', String(length=70)),
    Column('fonction', String(length=70)),
    Column('badge1', String(length=70)),
    Column('badge2', String(length=70)),
    Column('attestation_demandee', Boolean),
    Column('commentaire', String(length=200)),
    Column('inscription_repas_1', Boolean),
    Column('inscription_repas_2', Boolean),
)

personne = Table('personne', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('nom', VARCHAR(length=70), nullable=False),
    Column('prenom', VARCHAR(length=70)),
    Column('email', VARCHAR(length=70)),
    Column('telephone', VARCHAR(length=20)),
    Column('organisation', VARCHAR(length=70)),
    Column('fonction', VARCHAR(length=70)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['inscription'].columns['fonction'].create()
    post_meta.tables['inscription'].columns['organisation'].create()
    post_meta.tables['inscription'].columns['telephone'].create()
    pre_meta.tables['personne'].columns['fonction'].drop()
    pre_meta.tables['personne'].columns['organisation'].drop()
    pre_meta.tables['personne'].columns['telephone'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['inscription'].columns['fonction'].drop()
    post_meta.tables['inscription'].columns['organisation'].drop()
    post_meta.tables['inscription'].columns['telephone'].drop()
    pre_meta.tables['personne'].columns['fonction'].create()
    pre_meta.tables['personne'].columns['organisation'].create()
    pre_meta.tables['personne'].columns['telephone'].create()
