from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from . import db

# extend the UserMixin class to use the flask user manage function
class User(db.Model, UserMixin):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String)
    password = db.Column(db.String)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return "<User {} ID {}>".format(self.username, self.id)

    def is_authenticated(self):
        return True

    def is_actice(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):             # using the username as unique identifier
        return self.username



class Post(db.Model):
    __tablename__ = 'Post'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    category = db.Column(db.String)
    userid = db.Column(db.Integer, db.ForeignKey('User.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)




class Comment(db.Model):
    __tablename__ = 'Comment'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    body = db.Column(db.Text)
    userid = db.Column(db.Integer, db.ForeignKey('User.id'))
    postid = db.Column(db.Integer, db.ForeignKey('Post.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

db.create_all()
