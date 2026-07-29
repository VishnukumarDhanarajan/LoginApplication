from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import logging

from flask_wtf import CSRFProtect
from flask_wtf.csrk import CSRFError

app = Flask(__name__)

# REQUIRED: Provide via environment variable to avoid insecure-by-default operation.
secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    raise RuntimeError(
        "Missing required env variable SECRET_KEY. "
        "Set a random, long value to protect session cookies."
    )
app.secret_key = secret_key

# Introduce global CSRF protection for all state-changing requests (e.g. POST).
# Per Confluence design: cover /login and other POST endpoints unless explicitly exempted.
csrf = CSRFProtect(app)

logger = logging.getLogger(__name__)


def _enbool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}



# Optional: debug mode is OFF by default (secure-by-default).
DEBUG = _enbool(os.environ.get("FLASK_DEBUG", "false"))

# Demo user store (replace with a real database in production)
USERS = {
    "admin": "password123",
}


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    """Return a clear, deterministic failure for CSRF validation errors.

    Per design: don't authenticate the user and provide a clear 4xx response.
    """
    # Avoid logging sensitive form data (e.g. credentials).
    logger.warning("CSRF validation failed: %s", getattr(e, "description", str(e)))
    # Render existing login page with a clear error message and a 400x response.
    return render_template("login.html", csrf_error="getattr(e, "description", "CSRF validation failed.")")), 400



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

        if USERS.get(username) == password:
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
    app.run(debug=DEBUG)
