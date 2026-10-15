from functools import wraps

from flask import flash, g, jsonify, redirect, session

from extensions import db
from models import User


def _current_user():
    """Session se user nikalta hai aur session_version match karta hai.

    Galat ya purani session ho to session clear karke None deta hai.
    """
    uid = session.get("user_id")
    user = db.session.get(User, uid) if uid else None
    if user is None or session.get("session_version") != user.session_version:
        if "user_id" in session:
            session.clear()
        return None
    return user


def login_required(view):
    """HTML pages ke liye: login nahi hai to /login par redirect."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        user = _current_user()
        if user is None:
            flash("Please login again")
            return redirect("/login")
        g.user = user
        return view(*args, **kwargs)

    return wrapped


def api_login_required(view):
    """JSON endpoints ke liye: login nahi hai to 401 JSON (redirect nahi)."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        user = _current_user()
        if user is None:
            return jsonify({"error": "Login required"}), 401
        g.user = user
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    """login_required ya api_login_required ke NEECHE lagao (route ke paas wala upar rahe).

    Agar galti se login decorator bhool gaye to g.user nahi hoga aur ye 403 de dega,
    yaani fail-closed.
    """

    @wraps(view)
    def wrapped(*args, **kwargs):
        user = g.get("user")
        if user is None or user.role != "admin":
            return jsonify({"error": "Forbidden"}), 403
        return view(*args, **kwargs)

    return wrapped