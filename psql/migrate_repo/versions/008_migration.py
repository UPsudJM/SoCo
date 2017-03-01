from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
formulaire = Table('formulaire', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('id_evenement', Integer, nullable=False),
    Column('date_ouverture_inscriptions', Date, nullable=False),
    Column('date_cloture_inscriptions', Date, nullable=False),
    Column('organisateur_en_copie', Boolean),
    Column('champ_attestation', Boolean, default=ColumnDefault(True)),
    Column('champ_type_inscription', Boolean),
    Column('jour_par_jour', Boolean),
    Column('champ_restauration_1', Boolean),
    Column('texte_restauration_1', String(length=200)),
    Column('champ_restauration_2', Boolean),
    Column('texte_restauration_2', String(length=200)),
    Column('champ_libre_1', Boolean),
    Column('texte_libre_1', String(length=200)),
    Column('champ_libre_2', Boolean),
    Column('texte_libre_2', String(length=200)),
    Column('upd', DateTime)
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['formulaire'].columns['champ_libre_1'].create()
    post_meta.tables['formulaire'].columns['champ_libre_2'].create()
    post_meta.tables['formulaire'].columns['texte_libre_1'].create()
    post_meta.tables['formulaire'].columns['texte_libre_2'].create()
    post_meta.tables['formulaire'].columns['jour_par_jour'].create()
    #post_meta.tables['evenement'].columns['url'].create()
    #post_meta.tables['organisation'].columns['url'].create()
    #post_meta.tables['inscription'].columns['jours_de_presence'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['formulaire'].columns['champ_libre_1'].drop()
    post_meta.tables['formulaire'].columns['champ_libre_2'].drop()
    post_meta.tables['formulaire'].columns['texte_libre_1'].drop()
    post_meta.tables['formulaire'].columns['texte_libre_2'].drop()
    post_meta.tables['formulaire'].columns['jour_par_jour'].drop()
    #post_meta.tables['evenement'].columns['url'].drop()
    #post_meta.tables['organisation'].columns['url'].drop()
    #post_meta.tables['inscription'].columns['jours_de_presence'].drop()

