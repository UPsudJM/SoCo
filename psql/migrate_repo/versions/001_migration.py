from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
alembic_version = Table('alembic_version', pre_meta,
    Column('version_num', VARCHAR(length=32), nullable=False),
)

inscription = Table('inscription', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('id_evenement', Integer, nullable=False),
    Column('id_personne', Integer, nullable=False),
    Column('date_inscription', DateTime),
    Column('type_inscription', String(length=70)),
    Column('badge1', String(length=70)),
    Column('badge2', String(length=70)),
    Column('attestation_demandee', Boolean),
    Column('commentaire', String(length=200)),
    Column('inscription_repas_1', Boolean),
    Column('inscription_repas_2', Boolean),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['alembic_version'].drop()
    post_meta.tables['inscription'].columns['badge1'].create()
    post_meta.tables['inscription'].columns['badge2'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['alembic_version'].create()
    post_meta.tables['inscription'].columns['badge1'].drop()
    post_meta.tables['inscription'].columns['badge2'].drop()
