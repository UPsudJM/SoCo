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
    Column('jours_de_presence', String(length=10)),
    Column('commentaire', String(length=200)),
    Column('inscription_repas_1', Boolean),
    Column('inscription_repas_2', Boolean),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['inscription'].columns['jours_de_presence'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['inscription'].columns['jours_de_presence'].drop()
