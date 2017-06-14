
import os

from config.config import config

def database_url():
    env = os.getenv('PYTHON_ENV') or 'development'
    db  = config[env]['db']

    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(db['username'], db['password'], db['host'], db['port'], db['database'])

    return(url)
