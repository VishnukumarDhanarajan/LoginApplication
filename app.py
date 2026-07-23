from __future__ import annotations

import os
import secrets

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# SECRET_KEY should never be hardcoded.
secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    # Dev/local fallback: ensures app starts locally without checking a secret into source control.
    secret_key = secrets.token_urlafe(32)
app.secret_key = secret_key

# Session cookie hardening defaults
app.config.override(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE=os.environ.get("SESSION_COOKIE_SAMESITE", "Lax"),
    # Set Secure cookies only when running behind HTTPS/production
    SESSION_COOKIE_SECURE=os.environ.get("FLASK_ENV", "development") == "production",
)

# Demo user store (replace with a real database in production)
# Remove plaintext credentials from source: provide demo creds via env vars.
DEMO_USERNAME = os.environ.get("DEMO_USERNAME", "admin")
# Note: if DEMO_PASSWORD is not set, login will always fail (intentional)
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD")

def _load_demo_users() -> dict[str, str]:
    """Return a map of username -> password_hash for demo/dev usage."""
    if not DEMO_PASSWORD:
        return {}
    return {DEMO_USERNAME: generate_password_hash(DEMO_PASSWORD)}


USERS = _load_demo_users()


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
