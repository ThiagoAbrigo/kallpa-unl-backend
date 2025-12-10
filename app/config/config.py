from os import environ, path
from dotenv import load_dotenv
import urllib.parse

config_dir = path.abspath(path.dirname(__file__)) 
base_dir = path.abspath(path.join(config_dir, '..', '..')) 
load_dotenv(path.join(base_dir, '.env'))

class Config:
    #genaral configuration
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ.get('FLASK_ENV')
    
    # PostgreSQL config
    user = environ.get("PGUSER")
    password = environ.get("PGPASSWORD")
    host = environ.get("PGHOST")
    db = environ.get("PGDATABASE")
    port = environ.get("PGPORT", "5432")
    
    # URL encode password para evitar problemas con caracteres especiales
    encoded_password = urllib.parse.quote_plus(password) if password else ''
    
    print(f'postgresql://{user}:****@{host}:{port}/{db}')
    SECRET_KEY = environ.get("SECRET_KEY")
    JWT_SECRET_KEY = environ.get("JWT_SECRET_KEY")

    #SQLAlchemy configuration - usar psycopg (v3) en lugar de psycopg2
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg://{user}:{encoded_password}@{host}:{port}/{db}'
    
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_RECORS_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = 'enable'