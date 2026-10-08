from extensions import db
from datetime import datetime
from zoneinfo import ZoneInfo


class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(200),nullable=False)
    mobile=db.Column(db.String(20),nullable=False)
    password=db.Column(db.Integer,nullable=False)
    email=db.Column(db.String(200),nullable=False)
    age=db.Column(db.Integer,nullable=False)
    role=db.Column(db.String(20),nullable=False,default="user")
    orders=db.relationship("Order",backref="user",lazy=True)
    banks=db.relationship("Bank",backref="user",lazy=True)
    

class Order(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    product=db.Column(db.String,nullable=False)
    amount=db.Column(db.Integer,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")))

class Bank(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(200),nullable=False)
    account_no=db.Column(db.String(200),nullable=False)
    mobile_no=db.Column(db.String(20),nullable=False,unique=True)
    password=db.Column(db.String(200),nullable=False)
    amount=db.Column(db.Integer,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
