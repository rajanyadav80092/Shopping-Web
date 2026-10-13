from flask import url_for,Blueprint,render_template,redirect,request,flash,jsonify,session
from werkzeug.security import generate_password_hash,check_password_hash
from models import User
from extensions import db
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from functools import wraps


v1_auth=Blueprint("v1_auth",__name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")

        if user_id is None:
            return redirect(url_for("v1_auth.login"))

        user = db.session.get(User, user_id)

        if user is None:
            session.clear()
            return redirect(url_for("v1_auth.login"))

        if session.get("session_version") != user.session_version:
            session.clear()
            flash("Session expired. Please login again.")
            return redirect(url_for("v1_auth.login"))

        return view(*args, **kwargs)

    return wrapped

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
        session.clear()
        session["user_id"]=user.id
        session["session_version"]=user.session_version
        db.session.commit()
        return redirect("/orders")
    
    return render_template("/login.html")
    
@v1_auth.route("/change_password",methods=["POST"])
def change_password():
    if "user_id" not in session:
        return redirect("/login")
    user=User.query.filter_by(id=session["user_id"]).first()
    if not user:
        return jsonify({"error":"user not found"})
    old_password=request.form.get("old_password","")
    new_password=request.form.get("new_password","")
    check=check_password_hash(user.password,old_password)
    if not check:
        flash("your old password is wrong")
        return render_template("change_password.html")
    if len(new_password)<4:
        flash("password length smaller than 4")
        return render_template("change_password.html")
    password=generate_password_hash(new_password)
    user.password=password
    user.session_version+=1
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    session.clear()
    flash("password change login again")
    return redirect("/login")
    

    
    
@v1_auth.route("/madeadmin",methods=["POST"])
@login_required
def adminmakeuser():
    if "user_id" not in session:
        return redirect("/login")
    current_user = db.session.get(User, session["user_id"])

    if current_user is None:
        session.clear()
        return redirect("/login")

    if current_user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403
    
    id=request.form.get("id")
    if not id:
        return jsonify({"error":"empty box"})
    user=User.query.filter_by(id=id).first()
    if user and user.role=="admin":
        user.role="user"
        session["session_version"]+=1
        db.session.commit()
        flash("You are make admin to user")
        return redirect("/")
    if user:
        flash("only admin make user")
        return redirect("/")
    return jsonify({"error":"user not found"})
        
    
@v1_auth.route("/database")
def database():
    if "user_id" not in session:
        return render_template("login.html")
    current_user = db.session.get(User, session["user_id"])
    print(current_user)
    if current_user is None:
        session.clear()
        return redirect("/login")
    if current_user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403
    
    user=User.query.filter_by(id=session["user_id"]).first()
    if not user:
        return jsonify({"empty folder"})
    if user.role=="admin":
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