import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URI", f"sqlite:///{os.path.join(BASE_DIR, 'mechanic_shop.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 60
    RATELIMIT_STORAGE_URI = "memory://"


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
