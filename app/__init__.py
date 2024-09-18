from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set a secret key for your application
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import models, routes, helpers
