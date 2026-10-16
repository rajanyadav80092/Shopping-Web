from flask import Flask,jsonify,request,render_template,flash,redirect,session
from models import User
from extensions import db
from config import Config
from backend.auth import v1_auth
from backend.orders import v1_orders
from backend.upi import v1_upi
from flask_migrate import Migrate
from backend.decorator import api_login_required,admin_required
from backend.pagination_route import v1_lists



app=Flask(__name__)

app.config.from_object(Config)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///users.db"


app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    WTF_CSRF_ENABLED=True,
)
migrate=Migrate(app,db)

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(v1_auth,url_prefix="/backend")
app.register_blueprint(v1_orders,url_prefix="/backend")
app.register_blueprint(v1_upi,url_prefix="/backend")
app.register_blueprint(v1_lists,url_prefix="/backend")

@app.route("/")
def home():
    return render_template("/home.html")

@app.route("/login")
def login_page():
    return render_template("/login.html")

@app.route("/signup")
def signin_page():
    return render_template("/signup.html")

@app.route("/orders")
@api_login_required
def orders():
    if "user_id" in session:
        return render_template("/add_order.html")
    return redirect("/login")

@app.route("/changepassword")
@api_login_required
def changepass():
    return render_template("change_password.html")

@app.route("/makeadmin")
@api_login_required
@admin_required
def makeadmin():
    return render_template("adminmake.html")

@app.route("/settings")
@api_login_required
def setting():
    return render_template("settings.html")

@app.route("/adminmakeuser")
@api_login_required
@admin_required
def useradmin():
    return render_template("usermadeadmin.html")

@app.route("/addbank")
@api_login_required
def addbank():
    return render_template("bank.html")
if __name__ == "__main__":
    app.run(debug=True)
    