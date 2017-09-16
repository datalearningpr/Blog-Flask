
from flask_sqlalchemy import SQLAlchemy
from flask import Flask


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Blog.db"
db = SQLAlchemy(app)

import Blog.views
import Blog.models
import Blog.forms