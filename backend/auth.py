from flask import url_for,Blueprint,render_template,redirect,request,flash,jsonify,session
from werkzeug.security import generate_password_hash,check_password_hash
from models import User
from extensions import db
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError


v1_auth=Blueprint("v1_auth",__name__)


@v1_auth.route("/signup",methods=["POST"])
def signup():
    if request.method=="POST":
        name=request.form.get("name","").strip().lower()
        password=request.form.get("password","")
        mobile=request.form.get("mobile","").strip()
        email=request.form.get("email","").strip().lower()
        if not mobile.isdigit() or len(mobile) != 10:
            flash("check mobile number")
            return redirect("/signup")
        if len(password)<8:
            flash("Password is smaller than 8")
            return redirect("/signup")
        try:
            age = int(request.form.get("age", ""))
        except ValueError:
            flash("Invalid age")
            return redirect("/signup")
        if age<16 or age>120:
            flash("your age is less than 16")
            return redirect("/signup")
        password=generate_password_hash(password)
        is_count=User.query.count()==0
        user=User.query.filter(or_(email==User.email,mobile==User.mobile)).first()
        if user:
            flash("Please use unique email or mobile")
            return redirect("/signup")
        if len(name)<4:
            flash("your name length less tha 5")
            return redirect("/signup") 
        user=User(name=name,password=password,email=email,mobile=mobile,age=age,role="admin" if is_count else "user")
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Email or mobile already exists")
            return redirect("/signup")
        flash("your signin successfull")
        return redirect("/login")
    return render_template("/signup.html")

@v1_auth.route("/login",methods=["POST"])
def login():
    if request.method=="POST":
        identifier=request.form.get("identifier").strip().lower()
        password=request.form.get("password")
        user=User.query.filter(or_(
            identifier==User.name,
            identifier==User.email,
            identifier==User.mobile
        )).first()
        
        if not user:
            flash("user not found please put correct identaty")
            return render_template("login.html")
        
        if user and not check_password_hash(user.password,password):
            return jsonify({"incorrect":"Password"})
        user.role="admin"
        session["user_id"]=user.id
        session["user_role"]=user.role
        db.session.commit()
        return redirect("/orders")
    return render_template("/login.html")
    
@v1_auth.route("/adminmake/<int:id>")
def adminmakeuser(id):
    if "user_id" not in session:
        return redirect(url_for("v1_auth.login"))
    if session["user_role"]=="admin":
        user=User.query.filter_by(id=id).first()
        if not user:
            return jsonify({"error":"user not found"})
        if user.role=="admin":
            user.role="user"
            flash("You are make admin to user")
            return redirect("/")
        flash("this is also user")
        return redirect("/")
    flash("only admin make user and admin make user")
        
    
@v1_auth.route("/database")
def database():
    if "user_id" not in session:
        return render_template("login.html")
    user=User.query.filter_by(id=session["user_id"]).first()
    if not user:
        return jsonify({"empty folder"})
    if session["user_role"]=="admin":
        user=User.query.all()
        return jsonify([{
            "id":use.id,
            "name":use.name,
            "email":use.email,
            "mobile":use.mobile,
            "role":use.role
        } for use in user] )
        
    return jsonify([{
        "user_id":user.id,
        "name":user.name,
        "email":user.email,
        "mobile":user.mobile,
        "role":user.role
    }])
    
@v1_auth.route("/logout")
def logout():
    if "user_id" in session:
        session.clear()
        return render_template("/login.html")
    flash("first login")
    return render_template("/login.html")