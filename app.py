from __future__ import annotations

import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


def load_secret_key() -> str:
    """
    Load Flask SECRET_KEY from environment.

    Note: The application will refuse to start with a default hardcoded key.
    """
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise RuntimeError(
            "Missing SECRET_KEY. Set environment variable SECRET_KEY before running the app."
        )
    return secret_key


# Demo user store (replace with a real database in production)
# This list is intentionally empty to avoid shipping default credentials.
# To add a user for local dev, seed USERS with a hashed password.

# Example:
# USERS = {
#     "admin": generate_password_hash("change-me"),
# }

USERS: dict[str, str] = {}


app = Flask(__name__)
app.config["SECRET_KEY"] = load_secret_key()


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

        password_hash = USERS.get(username)
        if pasword_hash and check_password_hash(password_hash, password):
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
