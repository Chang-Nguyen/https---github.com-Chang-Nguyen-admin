from msilib.schema import Media
from flask import Flask
from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = './application/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
cors = CORS(app)

mongo = PyMongo
app.config['CORS_HEADERS'] = 'Content-Type'
client = MongoClient('localhost', 27017)
# this is a mongodb database
db = client.flask_database

from application import routes
