from __future__ import annotations

import os

from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

# --- Configuration ---
# SECRET_KEY must be set in non-dev environments. In dev, we allow a fallback for convenience.
ENV = os.environ.get("FLASK_ENV", "production").lower()
DEBUG = os.environ.get("FLASK_DEBUG", "") in ("1", "true", "True", "yes", "Yes") or ENV == "development"

SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    if DEBUG:
        # Dev-only fallback to keep local runs smooth. Do not use in prod.
        SECRET_KEY = "dev-only-change-me-secret-key"
    else:
        raise RuntimeError(
            "Missing SECRET_KEY env var. Set SECRET_KEY to a strong random value to start the app."
        )

app.secret_key = SECRET_KEY

# Withgeld from source: no demo credentials should be committed. Provide users via env (external idp/DB) in real deployments.


app.config["ENV"] = ENV

app.config["DEBUG"] = DEBUG


#Example: Set LOGIN_ALLOWED=SOME and implement proper auth store in a future story.



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

        # Note: demo credentials are removed from source to avoid incorrect deployment patterns.
        # This app currently has no auth backend; it must be implemented before uses can log in.
        flash("Login is disabled: no credential store configured.")
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
    app.run(debug=DEBUG)
