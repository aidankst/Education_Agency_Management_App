import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL')

SECRET_KEY = 'leveling-webapp'
SQLALCHEMY_DATABASE_URI = db_url

UPLOAD_FOLDER = '/upload_files'
ALLOWED_EXTENSIONS = {'pdf'}

STATIC_FOLDER = '/static'