from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
organisation = Table('organisation', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('nom', String(length=70), nullable=False),
    Column('interne', Boolean, default=ColumnDefault(False)),
    Column('email', String(length=70)),
    Column('logo', Binary),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['organisation'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['organisation'].drop()
