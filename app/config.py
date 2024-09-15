import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "school.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

