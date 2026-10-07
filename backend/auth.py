from flask import url_for,Blueprint,render_template,redirect,request,flash,jsonify,session
from werkzeug.security import generate_password_hash,check_password_hash
from models import User
from extensions import db
from sqlalchemy import or_


v1_auth=Blueprint("v1_auth",__name__)


@v1_auth.route("/signin",methods=["POST"])
def signin():
    if request.method=="POST":
        name=request.form.get("name")
        password=request.form.get("password")
        mobile=request.form.get("mobile")
        email=request.form.get("email")
        age=request.form.get("age")
        password=generate_password_hash(password)
        is_count=User.query.count()==6
        user=User(name=name,password=password,email=email,mobile=mobile,age=age,role="admin" if is_count else "user")
        db.session.add(user)
        db.session.commit()
        flash("your signin successfull")
        return redirect(url_for("v1_auth.database"))
    return render_template("/signin.html")

@v1_auth.route("/login",methods=["POST"])
def login():
    if request.method=="POST":
        identifier=request.form.get("identifier")
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
        session["user_id"]=user.id
        session["user_role"]=user.role
        db.session.commit()
        return redirect("/orders")
    
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