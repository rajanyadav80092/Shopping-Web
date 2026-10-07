from flask import Flask,jsonify,request,render_template,flash,redirect,session
from models import User
from extensions import db
from config import config
from backend.auth import v1_auth
from backend.orders import v1_orders
from backend.upi import v1_upi
from flask_migrate import Migrate

app=Flask(__name__)

app.config.from_object(config)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///users.db"


app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTONLY=True,
    SSESSION_COOKIE_SAMESITE="Lax",
    WTF_CSRF_ENABLES=True,
)
migrate=Migrate(app,db)

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(v1_auth,url_prefix="/backend")
app.register_blueprint(v1_orders,url_prefix="/backend")
app.register_blueprint(v1_upi,url_prefix="/backend")

@app.route("/")
def home():
    return render_template("/home.html")

@app.route("/login")
def login_page():
    return render_template("/login.html")

@app.route("/signin")
def signin_page():
    return render_template("/signin.html")

@app.route("/orders")
def orders():
    if "user_id" in session:
        return render_template("/add_order.html")
    return redirect("/login")
@app.route("/addbank")
def addbank():
    return render_template("bank.html")
if __name__ == "__main__":
    app.run(debug=True)
    