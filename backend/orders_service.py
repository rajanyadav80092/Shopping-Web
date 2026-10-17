"""place_order() aur cancel_order() — backend/orders_service.py me rakho.

Tumhare models.py ke naamon ke saath likha hai (Product.product, Product.exact_amount,
Order.quantity, Order.amount (ek item ka daam), Order.total_amount ...).

Zaroori: cancel_order() ko Order.status column chahiye. Models me ye line jodo:
    status = db.Column(db.String(20), nullable=False, default="placed", server_default="placed")
(server_default isliye ki purani rows wali table me migration NOT NULL column jod sake.)

Dhyan: ye code is sandbox me chalaya nahi gaya (yahan SQLAlchemy install nahi ho paaya).
Sirf syntax check hua aur stock/status wali SQL logic raw SQLite par test hui.
Apne project me pehle test order aur test cancel se check karo.
"""
from sqlalchemy import update

from extensions import db
from models import Order, Product

ALLOWED_PAYMENT_METHODS = ("cod", "upi")


class ProductUnavailable(Exception):
    """Product hai nahi ya band (is_active=False) hai."""


class OutOfStock(Exception):
    """Itna stock nahi bacha."""


class OrderNotFound(Exception):
    """Order hai nahi, ya is user ka nahi hai."""


class CannotCancel(Exception):
    """Order ab cancel nahi ho sakta (shipped/delivered ya pehle hi cancelled)."""


def final_unit_amount(product):
    """MRP me se discount ghata ke final daam.

    Dhyan: // integer division hai. Agar amount rupee me hai to paise wali fraction kat jaati hai
    (Rs 49 par 15% off = Rs 41.65 ki jagah 41). Isliye paise me rakhna behtar hai (Rs 49 = 4900).
    """
    return product.exact_amount * (100 - product.discount_percentage) // 100


def place_order(user_id, product_id, quantity, payment_method="cod"):
    """Order banata hai aur stock ghatata hai, dono ek hi transaction me.

    Client se sirf product_id aur quantity lo. Daam hamesha yahan DB se aata hai.

    Stock wala UPDATE atomic hai (WHERE stock >= quantity). Aakhri item par do log ek saath
    order karein to sirf ek ka UPDATE lagta hai, dusre ko OutOfStock milta hai.
    Pehle SELECT karke phir stock-1 likhne par dono jeet jaate (overselling).
    """
    if payment_method not in ALLOWED_PAYMENT_METHODS:
        raise ValueError("payment_method cod ya upi hona chahiye")
    if not isinstance(quantity, int) or not 1 <= quantity <= 50:
        raise ValueError("quantity 1 se 50 ke beech honi chahiye")

    item = db.session.get(Product, product_id)
    if item is None or not item.is_active:
        raise ProductUnavailable()

    result = db.session.execute(
        update(Product)
        .where(
            Product.id == product_id,
            Product.is_active.is_(True),
            Product.stock >= quantity,
        )
        .values(stock=Product.stock - quantity)
    )
    if result.rowcount != 1:
        db.session.rollback()
        raise OutOfStock()

    unit = final_unit_amount(item)
    order = Order(
        user_id=user_id,
        product_id=item.id,
        product=item.product,
        amount=unit,  # ek item ka final daam (snapshot); total_amount = amount * quantity
        total_amount=unit * quantity,
        quantity=quantity,
        payment_method=payment_method,
    )
    db.session.add(order)
    db.session.commit()
    return order


def cancel_order(user_id, order_id):
    """Sirf "placed" order cancel hota hai, aur stock wapas badhta hai.

    status badalne wala UPDATE bhi atomic hai (WHERE status = 'placed'), isliye double click
    ya do request ek saath aayein to stock do baar wapas nahi judta.

    Paid UPI order ka paisa wapas karna alag kaam hai (gateway se refund). Ye function
    sirf order aur stock sambhalta hai.
    """
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if order is None:
        raise OrderNotFound()

    flipped = db.session.execute(
        update(Order)
        .where(Order.id == order.id, Order.status == "placed")
        .values(status="cancelled")
    )
    if flipped.rowcount != 1:
        db.session.rollback()
        raise CannotCancel()

    db.session.execute(
        update(Product)
        .where(Product.id == order.product_id)
        .values(stock=Product.stock + order.quantity)
    )
    db.session.commit()
    return order