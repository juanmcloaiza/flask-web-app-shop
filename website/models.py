from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(10000))
    pic_uri = db.Column(db.String(150))
    price = db.Column(db.Integer)
    date_added = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id         = db.Column(db.Integer, primary_key=True)
    email      = db.Column(db.String(150), unique=True)
    password   = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    address    = db.Column(db.String(10000))
    products   = db.relationship('Product')
