from extensions import db
from datetime import datetime
from zoneinfo import ZoneInfo


class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(200),nullable=False)
    mobile=db.Column(db.String(20),nullable=False,unique=True)
    password=db.Column(db.String(255),nullable=False)
    email=db.Column(db.String(200),nullable=False,unique=True)
    age=db.Column(db.Integer,nullable=False)
    session_version=db.Column(db.Integer,nullable=False,default=0)
    role=db.Column(db.String(20),nullable=False,default="user")
    orders=db.relationship("Order",backref="user",lazy=True)
    banks=db.relationship("Bank",backref="user",lazy=True)
    product=db.relationship("Product",backref="user",lazy=True)
    
    

class Order(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    product=db.Column(db.String,nullable=False)
    amount=db.Column(db.Integer,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    quatity=db.Column(db.Integer,nullable=False)
    created_at = db.Column(db.DateTime,nullable=False,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")))
    payment_method=db.Column(db.String(20),nullable=False,default="none")
    payment_status=db.Column(db.String(20),default="Pending",nullable=False)
    payment_id=db.Column(db.String(255),nullable=True,default="none")
    refund_status=db.Column(db.String(20),default="None",nullable=False)
    refund_id=db.Column(db.String(255),nullable=True,default="none")
    

class Bank(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(200),nullable=False)
    account_no=db.Column(db.String(200),nullable=False,unique=True)
    mobile_no=db.Column(db.String(20),nullable=False)
    password=db.Column(db.String(200),nullable=False)
    amount=db.Column(db.Integer,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)


class Product(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    product=db.Column(db.String(150),nullable=False)
    exact_amount=db.Column(db.Integer,nullable=False)
    stock=db.Column(db.Integer,nullable=False)
    discount_percentage=db.Column(db.Integer,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    