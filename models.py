from datetime import datetime as dt
from flask_login import UserMixin
from app import  db


class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    likes = db.Column(db.Integer)
    dislikes = db.Column(db.Integer)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=dt.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Articles %r>' % self.id


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(32), nullable=False, unique=False)
    password = db.Column(db.String(255), nullable=False)
    lastSeen = db.Column(db.DateTime)
    lastVisit = db.Column(db.DateTime)  # try to migrate to ActionEvent


class ActionEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    action = db.Column(db.String(32), nullable=False)
    date = db.Column(db.DateTime, default=dt.utcnow)


db.create_all()