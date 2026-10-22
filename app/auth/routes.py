
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from app.auth import auth_bp
from app.models import User


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template("auth/login.html"), 400

        user = User.query.filter_by(username=username).first()

        if (
            user is None
            or not user.is_active
            or not check_password_hash(user.password_hash, password)
        ):
            flash("Invalid username or password.", "error")
            return render_template("auth/login.html"), 401

        login_user(user, remember=False)
        flash("Login successful.", "success")

        next_page = request.args.get("next")
        if next_page and next_page.startswith("/") and not next_page.startswith("//"):
            return redirect(next_page)

        return redirect(url_for("auth.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("auth/dashboard.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
