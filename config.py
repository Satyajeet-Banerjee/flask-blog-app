import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set in environment variables")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///posts.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print("⚠️ Warning: Mail credentials not set")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False