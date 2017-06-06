"""
Usage: in web2py models/db.py

from gluon.contrib.heroku import get_db
db = get_db()

"""
import os
from gluon import *
from pydal.adapters import ADAPTERS, PostgreSQLAdapter
from pydal.helpers.classes import UseDatabaseStoredFile
import logging
logger = logging.getLogger("web2py.app.ipos")
logger.setLevel(logging.DEBUG)

class HerokuPostgresAdapter(UseDatabaseStoredFile,PostgreSQLAdapter):
    drivers = ('psycopg2',)
    uploads_in_blob = True

ADAPTERS['postgres'] = HerokuPostgresAdapter

def get_db(name = None, pool_size=10):
    logger.info(os.environ[name])
    if not name:
        names = [n for n in os.environ.keys()
                 if n[:18]+n[-4:]=='HEROKU_POSTGRESQL__URL']
        if names:
            name = names[0]
            logger.info("Using db " + name)
    if name and os.environ[name] == 'sqlite_local':
        db = DAL('sqlite://heroku.test.sqlite')
        logger.info('sqlite_local set, using sqlite')
    elif name:
        db = DAL(os.environ[name], pool_size=pool_size)
        current.session.connect(current.request, current.response, db=db)
        logger.info('Using postgres db')
    else:
        db = DAL('sqlite://heroku.test.sqlite')
        logger.info('Unable to find postgres db, using sqlite')
    return db
