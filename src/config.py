import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "372908b2c18c3c89ea3c3486a6aee2d1d4ca2f41b0aed3f84bdbd08b518c3e53")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-token")


    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///clinic.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False