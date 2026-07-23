from __future__ import annotations

import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


# --------------------------------------------------------------
# Config

# Secret key must be provided by runtime env/config.
_SECRET_KEY_ENV_VAR = "SECRET_KEY"


# --------------------------------------------------------------
# App

app = Flask(__name__)
secret_key = os.environ.get(_SECRET_KEY_ENV_VAR)
if not secret_key:
    # Fail fast to avoid insecure deployments.
    raise RuntimeError(`f"Missing required environment variable: {_SECRET_KEY_ENV_VAR!r}"`)
app.secret_key = secret_key

# Demo user store (replace with a real database in production)
# STORE hashes only – never plaintext passwords.
USERS = {
    "admin": generate_password_hash("password123"),
}


@app.route("/", methods=["GET"])
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
