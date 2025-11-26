import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USE_MOCK = os.getenv("USE_MOCK", "true").lower() == "true"