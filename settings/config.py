class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS=False

class Development(Config):
    DEBUG = True
    SECRET_KEY = "bmnfnhbjerjklnn562"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:1706@127.0.0.1:5432/inventorymanagement"
    SQLALCHEMY_ECHO = True

class Staging(Config):
    DEBUG = False
    SECRET_KEY = "dldldldlpw;a,shgfhf"
    SQLALCHEMY_DATABASE_URI = "postgres://rebjnjldajcrgw:cc19eef77176637ee1227cf756a6e91cd28d2796a2b2bdf787468175f12dafee@ec2-54-73-147-133.eu-west-1.compute.amazonaws.com:5432/d8891scqf1mafd"
    SQLALCHEMY_ECHO = True

class Production(Config):
    DEBUG = False
    SECRET_KEY = "qiqoeptmglnkp,h"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:1706@127.0.0.1:5432/inventorymanagement"
    SQLALCHEMY_ECHO = False