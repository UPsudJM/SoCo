from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
personne_organisation = Table('personne_organisation', post_meta,
    Column('id_personne', Integer),
    Column('id_organisation', Integer),
)

evenement = Table('evenement', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('logo', String(length=200), default=ColumnDefault('logo.png')),
    Column('titre', String(length=200)),
    Column('sstitre', String(length=200)),
    Column('date', Date),
    Column('date_fin', Date),
    Column('lieu', String(length=400)),
    Column('resume', Text),
    Column('gratuite', Boolean, default=ColumnDefault(True)),
    Column('uid_organisateur', String(length=100)),
    Column('id_entite_organisatrice', Integer),
    Column('upd', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['personne_organisation'].create()
    post_meta.tables['evenement'].columns['id_entite_organisatrice'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['personne_organisation'].drop()
    post_meta.tables['evenement'].columns['id_entite_organisatrice'].drop()
