from flask import Blueprint,url_for,jsonify,render_template,redirect,request,session,flash
from extensions import db
from models import Order,Bank


v1_orders=Blueprint("v1_orders",__name__)


@v1_orders.route("/add-order",methods=["POST"])
def orders_post():
    if "user_id" not in session:
        return render_template("/login.html")
    
    if request.method=="POST":
        product=request.form.get("product")
        amount=request.form.get("amount")
        bank=Bank.query.filter_by(user_id=session["user_id"]).first()
        if not bank:
            flash("first add your bank")
            return redirect("/addbank")
            
        if not amount:
            return jsonify({"error": "Amount is required"}), 400
        try:
            amount = int(amount)
        except ValueError:
            return jsonify({"error": "Amount must be a valid integer"}), 400
        if bank.amount<amount:
            flash("your amount is low ")
            return redirect("/orders")
        
        bank.amount-=amount
        order=Order(amount=amount,product=product,user_id=session["user_id"])
        db.session.add(order)
        db.session.commit()
        jsonify({"success":"your order add successfully"})
        return redirect(url_for("v1_orders.allorder"))
    return redirect("/orders")

@v1_orders.route("/allorder",methods=["GET"])
def allorder():
    users=Order.query.all()
    if session["user_role"]=="admin":
        return jsonify([{
            "order_id":user.id,
            "order_amount":user.amount,
            "order_product":user.product,
            "user_id":user.user_id,
            "date": user.created_at.strftime("%Y-%m-%d"),
            "time": user.created_at.strftime("%H:%M:%S"),
            "day": user.created_at.strftime("%A")
        }   for user in users])
        
    users=Order.query.filter_by(user_id=session["user_id"]).all()
    return jsonify([{
                "order_id":user.id,
                "order_amount":user.amount,
                "order_product":user.product,
                "user_id":user.user_id,
                "date": user.created_at.strftime("%Y-%m-%d"),
                "time": user.created_at.strftime("%H:%M:%S"),
                "day": user.created_at.strftime("%A")
            } for user in users])
@v1_orders.route("/allorder/<int:user_id>")
def allorderbyuser(user_id: int):
    if session["user_role"]=="admin":
        order=Order.query.filter_by(user_id=user_id).all()
        return jsonify([{
            "order_id":user.id,
            "order_amount":user.amount,
            "order_product":user.product,
            "user_id":user.user_id,
            "date": user.created_at.strftime("%Y-%m-%d"),
            "time": user.created_at.strftime("%H:%M:%S"),
            "day": user.created_at.strftime("%A")
        }   for user in order])
        
    return redirect(url_for("v1_orders.allorder"))
