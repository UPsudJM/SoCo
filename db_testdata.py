#!/usr/bin/env python3
from migrate.versioning import api
from config import SQLALCHEMY_MIGRATE_REPO

from soco import SQLALCHEMY_DATABASE_URI
from soco import test_data
test_data()

