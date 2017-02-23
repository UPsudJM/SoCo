from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
evenement = Table('evenement', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('titre', String(length=200)),
    Column('sstitre', String(length=200)),
    Column('date', Date),
    Column('date_fin', Date),
    Column('lieu', String(length=400)),
    Column('resume', Text),
    Column('gratuite', Boolean, default=ColumnDefault(True)),
    Column('uid_organisateur', String(length=100)),
    Column('id_entite_organisatrice', Integer),
    Column('logo', String(length=200)),
    Column('url', String(length=200)),
    Column('upd', DateTime)
)

organisation = Table('organisation', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('nom', String(length=70), nullable=False),
    Column('interne', Boolean, default=ColumnDefault(False)),
    Column('email', String(length=70)),
    Column('logo', String(length=200)),
    Column('url', String(length=200)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['evenement'].columns['url'].create()
    post_meta.tables['organisation'].columns['url'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['evenement'].columns['url'].drop()
    post_meta.tables['organisation'].columns['url'].drop()
