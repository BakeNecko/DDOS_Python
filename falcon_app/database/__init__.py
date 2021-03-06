# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from falcon_app import log
from falcon_app import config

LOG = log.get_logger()


def get_engine(uri):
    LOG.info("Connecting to database..")
    options = {
        "pool_recycle": 3600,
        "pool_size": 10,
        "pool_timeout": 30,
        "max_overflow": 30,
        "echo": config.DB_ECHO,
        "execution_options": {"autocommit": config.DB_AUTOCOMMIT},
    }
    return create_engine(uri, **options)


db_session = scoped_session(sessionmaker())
engine = get_engine(config.DATABASE_URL)


def init_session():
    db_session.configure(bind=engine)
