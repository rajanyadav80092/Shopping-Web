from flask import Blueprint,url_for,jsonify,render_template,redirect,request,session,flash
from extensions import db
from models import Order,Bank


v1_orders=Blueprint("v1_orders",__name__)


@v1_orders.route("/add-order",methods=["POST"])
def orders_post():
    if "user_id" not in session:
        return render_template("/login.html")
    
    if request.method=="POST":
        product=request.form.get("product","").strip().lower()
        amount=request.form.get("amount","").strip().lower()
        payment_method=request.form.get("payment_method","").strip().lower()
        print(payment_method)
        if payment_method=="cod":
            order=Order(amount=amount,product=product,user_id=session["user_id"],payment_method=payment_method)
            db.session.add(order)
            db.session.commit()
            flash("your order add successfully")
            return redirect(url_for("v1_orders.allorder"))
        else:
            order=Order(product=product,
                        amount=amount,
                        user_id=session["user_id"],
                        payment_method="upi",
                        payment_id="12345",
                        payment_status="complete"
                    )
            db.session.add(order)
            db.session.commit()
            flash("your order booked")
            return redirect("/orders")
            
            
    
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
            "day": user.created_at.strftime("%A"),
            "payment_method":user.payment_method,
            "payment_status":user.payment_status,
            "payment_id":user.payment_id,
            "refund_id":user.refund_id,
            "refund_status":user.refund_status
            } for user in users])
        
    users=Order.query.filter_by(user_id=session["user_id"]).all()
    return jsonify([{
                "order_id":user.id,
                "order_amount":user.amount,
                "order_product":user.product,
                "user_id":user.user_id,
                "date": user.created_at.strftime("%Y-%m-%d"),
                "time": user.created_at.strftime("%H:%M:%S"),
                "day": user.created_at.strftime("%A"),
                "payment_method":user.payment_method,
                "payment_status":user.payment_status,
                "payment_id":user.payment_id,
                "refund_id":user.refund_id,
                "refund_status":user.refund_status
            } for user in users])
@v1_orders.route("/allorder/<int:user_id>")
def allorderbyuser(user_id: int):
    if "user_id" not in session:
        flash("first Login")
        return redirect("/login")
    if session["user_role"]=="admin":
        order=Order.query.filter_by(user_id=user_id).all()
        return jsonify([{
            "order_id":user.id,
            "order_amount":user.amount,
            "order_product":user.product,
            "user_id":user.user_id,
            "date": user.created_at.strftime("%Y-%m-%d"),
            "time": user.created_at.strftime("%H:%M:%S"),
            "day": user.created_at.strftime("%A"),
            "payment_method":user.payment_method,
            "payment_status":user.payment_status,
            "payment_id":user.payment_id,
            "refund_id":user.refund_id,
            "refund_status":user.refund_status
        }   for user in order])
        
    return redirect(url_for("v1_orders.allorder"))
