#import os
#from dotenv import load_dotenv

#load_dotenv()  # Load environment variables from .env

#class Config:
    #SECRET_KEY = os.environ.get("SECRET_KEY", "your_default_secret_key")
    #SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://localhost:5432/products_db")
    #SQLALCHEMY_TRACK_MODIFICATIONS = False

import os
from dotenv import load_dotenv

# Load .env only if not in production (i.e., locally)
if os.environ.get("FLASK_ENV") != "production":
    load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "your_default_secret_key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://localhost:5432/products_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Debug: print DATABASE_URL at app startup to verify correct env var is loaded
print("Using DATABASE_URL:", os.environ.get("DATABASE_URL"))
