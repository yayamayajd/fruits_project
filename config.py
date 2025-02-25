import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  
    SQLALCHEMY_ECHO = False  
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False  



    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")



    JSON_SORT_KEYS = False  
    JSONIFY_PRETTYPRINT_REGULAR = True  
