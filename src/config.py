import os

from dotenv import load_dotenv


load_dotenv()


def get_database_url():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return "sqlite:///clinic.db"

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return database_url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "372908b2c18c3c89ea3c3486a6aee2d1d4ca2f41b0aed3f84bdbd08b518c3e53")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "ff06d4b07453493661f79ab91f1388ddf15da487b7ef231015b09a2f3815baf7")


    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
