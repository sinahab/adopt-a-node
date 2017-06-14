
import os

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager

from config.config import config

def database_url():
    env = os.getenv('PYTHON_ENV') or 'development'
    db  = config[env]['db']

    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(db['username'], db['password'], db['host'], db['port'], db['database'])

    return(url)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    url = database_url()
    engine = create_engine(url, pool_size=20, max_overflow=0, client_encoding='utf8')

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
