from flask import Blueprint,url_for,redirect,render_template,jsonify,session,request,flash
from werkzeug.security import generate_password_hash,check_password_hash
from extensions import db
from models import Bank

v1_upi=Blueprint("v1_upi",__name__)

@v1_upi.route("/addbank",methods=["POST"])
def addbank_account():
    if "user_id" in session:
        name=request.form.get("name")
        mobile=request.form.get("mobile")
        account=request.form.get("account")
        amount=request.form.get("amount")
        if not amount:
            return jsonify({"error": "Amount is required"}), 400
        try:
            amount = int(amount)
        except ValueError:
            return jsonify({"error": "Amount must be a valid integer"}), 400
        password=request.form.get("password")
        bank=Bank(name=name,user_id=session["user_id"],password=generate_password_hash(password),amount=amount,account_no=account,mobile_no=mobile)
            
        db.session.add(bank)
        db.session.commit()
        flash("your bank detail successfully inter")
        return redirect("/orders")
    return redirect("/login")

@v1_upi.route("/bankdetail")
def bankdetail():
    if "user_id" in session:
        bank=Bank.query.filter_by(user_id=session["user_id"]).first()
        return jsonify({
            "id":bank.id,
            "name":bank.name,
            "amount":bank.amount,
            "account":bank.account_no,
            "user_id":bank.user_id
        })