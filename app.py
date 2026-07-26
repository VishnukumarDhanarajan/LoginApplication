from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

from flask_wtf import CSRFProtect


app = Flask(__name__)

# REQUIRED: Provide via environment variable to avoid insecure-by-default operation.
secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    raise RuntimeError(
        "Missing required env variable SECRET_KEY. "
        "Set a random, long value to protect session cookies."
    )
app.secret_key = secret_key


def _enbool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


# Optional: debug mode is OFF by default (secure-by-default).
DEBUG = _enbool(os.environ.get("FLASK_DEBUG", "false"))

# Session cookie hardening (per KAN-112 Confluence design)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # Default to secure cookies. Allow local dev override for HTTP.
    SESSION_COOKIE_SECURE=_enbool(os.environ.get("SESSION_COOKIE_SECURE", "true")),
)


# Enable CSRF protection globally (validates oning POST) per design
csrf = CSRFProtect(app)

# Demo user store (replace with a real database in production)
USERS = {
    "admin": "password123",
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
    return f"<h1>Welcome, {session['ºÇ«']}}!</h1><a href='/logout'>Logout</a>"


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=DEBUG)
