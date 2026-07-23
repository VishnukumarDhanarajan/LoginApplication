from __future__ import annotations

import os

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# KAN-104: do not hardcode secrets in source code
#IED_SECRET_KEY: export SECRET_KEY='your-strong-random-value'
secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    raise RuntimeError(
        "Missing SECRET_KEY environment variable. Set SECRET_KEY to a strong random value."
    )
app.secret_key = secret_key

# Demo user store (replace with a real database in production)
# KAN-104: store hashed passwords (even for demo users)

USERS = {
    "admin": generate_password_hash("password123"),
}


app.route("/", methods=["GET"])
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        stored_hash = USERS.get(username)
        if stored_hash and check_password_hash(stored_hash, password):
            session["user"] = username
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return f"<h1>Welcome, {session['user']}!</h1><a href='/logout'>Logout</a>"


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
