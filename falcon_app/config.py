# -*- coding: utf-8 -*-

import os


BRAND_NAME = "Falcon REST API Template"

APP_ENV = os.environ.get("APP_ENV") or "local"  # or 'live' to load live

POSTGRES = {
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'dbname': 'demo',
    'port': '5432',
}

DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/demo'

DB_ECHO = True

DB_AUTOCOMMIT = False

LOG_LEVEL = 'DEBUG'
