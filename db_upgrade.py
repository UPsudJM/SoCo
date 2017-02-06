#!/usr/bin/env python3
from migrate.versioning import api
from config import SQLALCHEMY_MIGRATE_REPO
from soco import SQLALCHEMY_DATABASE_URI

api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
print('Current database version: ' + str(v))
