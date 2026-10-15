"""Orders aur users ki paginated listing (offset + cursor dono).

Register karo:
    from paginated_routes import v1_lists
    app.register_blueprint(v1_lists, url_prefix="/backend")

Endpoints:
    GET /backend/orders/offset?page=1&per_page=20
    GET /backend/orders/cursor?cursor=<last id>&limit=20
    GET /backend/users/offset?page=1&per_page=20          (admin only)
    GET /backend/users/cursor?cursor=<last id>&limit=20   (admin only)

Ye purane /allorder, /allorder/<user_id> aur /database ki jagah lete hain.
"""

from flask import Blueprint, g, jsonify, request

from backend.decorator import admin_required, api_login_required
from models import Order, User
from pagination import (
    DEFAULT_PER_PAGE,
    MAX_ID,
    MAX_PAGE,
    MAX_PER_PAGE,
    PaginationError,
    cursor_paginate,
    offset_paginate,
    parse_int,
)

v1_lists = Blueprint("v1_lists", __name__)


@v1_lists.errorhandler(PaginationError)
def bad_pagination_params(err):
    return jsonify({"error": str(err)}), 400


def order_to_dict(o):
    return {
        "order_id": o.id,
        "user_id": o.user_id,
        "product": o.product,
        "amount": o.amount,
        "date": o.created_at.strftime("%Y-%m-%d"),
        "time": o.created_at.strftime("%H:%M:%S"),
        "day": o.created_at.strftime("%A"),
        "payment_method": o.payment_method,
        "payment_status": o.payment_status,
        "payment_id": o.payment_id,
        "refund_status": o.refund_status,
        "refund_id": o.refund_id,
    }


def user_to_dict(u):
    # password hash kabhi nahi bhejte
    return {"id": u.id, "name": u.name, "email": u.email, "mobile": u.mobile, "role": u.role}


def _orders_query():
    """Normal user ko sirf apne orders. Admin ko sab, aur chahe to ?user_id= se filter."""
    query = Order.query
    if g.user.role != "admin":
        # client ka bheja hua user_id yahan kabhi nahi padha jaata
        return query.filter(Order.user_id == g.user.id)
    uid = parse_int(request.args.get("user_id"), "user_id", default=None, maximum=MAX_ID, clamp=False)
    if uid is not None:
        query = query.filter(Order.user_id == uid)
    return query


def _page_args():
    page = parse_int(request.args.get("page"), "page", default=1, maximum=MAX_PAGE, clamp=False)
    per_page = parse_int(request.args.get("per_page"), "per_page", default=DEFAULT_PER_PAGE, maximum=MAX_PER_PAGE)
    return page, per_page


def _cursor_args():
    cursor = parse_int(request.args.get("cursor"), "cursor", default=None, maximum=MAX_ID, clamp=False)
    limit = parse_int(request.args.get("limit"), "limit", default=DEFAULT_PER_PAGE, maximum=MAX_PER_PAGE)
    return cursor, limit


# ---------- orders ----------

@v1_lists.route("/orders/offset")
@api_login_required
def orders_offset():
    page, per_page = _page_args()
    rows, meta = offset_paginate(_orders_query(), Order.id, page, per_page)
    return jsonify({"items": [order_to_dict(o) for o in rows], **meta})


@v1_lists.route("/orders/cursor")
@api_login_required
def orders_cursor():
    cursor, limit = _cursor_args()
    rows, meta = cursor_paginate(_orders_query(), Order.id, cursor, limit)
    return jsonify({"items": [order_to_dict(o) for o in rows], **meta})


# ---------- users (admin only) ----------

@v1_lists.route("/users/offset")
@api_login_required
@admin_required
def users_offset():
    page, per_page = _page_args()
    rows, meta = offset_paginate(User.query, User.id, page, per_page, descending=False)
    return jsonify({"items": [user_to_dict(u) for u in rows], **meta})


@v1_lists.route("/users/cursor")
@api_login_required
@admin_required
def users_cursor():
    cursor, limit = _cursor_args()
    rows, meta = cursor_paginate(User.query, User.id, cursor, limit, descending=False)
    return jsonify({"items": [user_to_dict(u) for u in rows], **meta})