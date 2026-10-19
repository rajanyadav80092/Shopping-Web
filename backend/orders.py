from flask import Blueprint,url_for,jsonify,render_template,redirect,request,session,flash
from extensions import db
from models import Order,Bank,User
from backend.decorator import api_login_required,admin_required

v1_orders=Blueprint("v1_orders",__name__)


@v1_orders.route("/add-order",methods=["POST"])
def orders_post():
    if "user_id" not in session:
        return render_template("/login.html")
    
    if request.method=="POST":
        product=request.form.get("product","").strip().lower()
        amount=float(request.form.get("amount"))
        quantity=int(request.form.get("quantity",1))
        print("quantity",type(amount))
        if quantity<=0:
            return jsonify({"error":"your quantity invalid"})
        payment_method=request.form.get("payment_method","").strip().lower()
        total_amount=amount*quantity
        if not total_amount:
            return jsonify({"error":"total amount is None"})
        if payment_method=="cod":
            order=Order(amount=amount,product=product,user_id=session["user_id"],payment_method=payment_method,total_amount=total_amount,quantity=quantity,product_id=1)
            try:
                db.session.add(order)
                db.session.commit()
                return redirect("/orders")
            except Exception:
                db.session.rollback()
                raise
        else:
            total_amount=amount*quantity
            order=Order(product=product,
                        amount=amount,
                        user_id=session["user_id"],
                        payment_method="upi",
                        payment_id="12345",
                        payment_status="complete",
                        total_amount=total_amount,
                        product_id=1,
                        quantity=quantity
                    )
            try:
                db.session.add(order)
                db.session.commit()
                return redirect("/orders")
            except Exception:
                db.session.rollback()
                raise
            
            
            
    
    return redirect("/orders")

@v1_orders.route("/allorder",methods=["GET"])
def allorder():
    if "user_id" not in session:
        return "first login"
    users=User.query.filter_by(id=session["user_id"]).first()
    if not users:
        return jsonify({"error":"order not found"})
    
    if users.role=="admin":
        orders=Order.query.filter_by().all()
        if not orders:
            return jsonify({"error":"order not in database"})
        return jsonify([{
            "total_order_id":user.id,
            "current_order_id":j+1,
            "order_amount":user.amount,
            "order_product":user.product,
            "user_id":user.user_id,
            "date": user.created_at.strftime("%Y-%m-%d"),
            "time": user.created_at.strftime("%H:%M:%S"),
            "day": user.created_at.strftime("%A"),
            "payment_method":user.payment_method,
            "payment_status":user.payment_status,
            "payment_id":user.payment_id,
            "refund_status":user.refund_status,
            "total_amount":user.total_amount,
            "refund_id":user.refund_id
            } for j,user in enumerate(orders)])
        
    orders=Order.query.filter_by(user_id=session["user_id"]).all()
    if not orders:
        return jsonify({"error":"not order"})
    return jsonify([{
                "order_id":user.id,
                "order_amount":user.amount,
                "current_order_id":j+1,
                "order_product":user.product,
                "user_id":user.user_id,
                "date": user.created_at.strftime("%Y-%m-%d"),
                "time": user.created_at.strftime("%H:%M:%S"),
                "day": user.created_at.strftime("%A"),
                "payment_method":user.payment_method,
                "payment_status":user.payment_status,
                "payment_id":user.payment_id,
                "refund_status":user.refund_status,
                "total_amount":user.total_amount,
                "refund_id":user.refund_id,
                "quantity":user.quantity
            } for j,user in enumerate(orders)])
    
@v1_orders.route("/allorder/<int:user_id>")
@api_login_required
def allorderbyuser(user_id: int):
    if "user_id" not in session:
        flash("first Login")
        return redirect("/login")
    if session["user_role"]=="admin":
        order=Order.query.filter_by(user_id=user_id).all()
        return jsonify([{
            "total_order_id":user.id,
            "current_order_id":j+1,
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
        }   for j,user in enumerate(order)])
        
    return redirect(url_for("v1_orders.allorder"))

@v1_orders.route("/return",methods=["POST"])
@api_login_required
def returnorder():
    if "user_id" not in session:
        flash("first login than return order")
        return redirect("/login")
    user_id=session["user_id"]
    id=request.form.get("id")
    if not id:
        return redirect("/cancel")
    
    order=Order.query.filter_by(id=id,user_id=user_id).first()
    if not order:
        flash("order id not exist")
        return redirect("/orders")
    order.refund_id="12343"
    order.refund_status="successfull"
    db.session.add(order)
    db.session.commit()
    flash("your order return successfully")
    return redirect("/orders")