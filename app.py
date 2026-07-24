import os

from flask import Flask, render_template, request, redirect, url_for, session, flash


app = Flask(__name__)


# --- Configuration (KAN-106) ---

# Secret is required to sign session cookies. Do not hardcode it in source code.
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Cookie hardening - safe defaults for production, but overrideable for local dev
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE", "true").strip().lower() in {"1", "true", "yes", "y", "on"}

# Debug is env-driven and disabled by default
_debug = os.getenv("FLASK_DEBUG", "false").strip().lower() in {"1", "true", "yes", "y", "on"}

# Fail fast in non-debug mode if SECRET_KEY is missing (don't start with an insecure fallback)
if not _debug and not app.config.get("SECRET_KEY"):
    raise RuntimeError(
        "Missing required env var: SECRET_KEY. Set a cryptographically strong value in production (e.g. 64+ random bytes). "
        "For local dev, you can set FLASK_DEBUG=true to bypass this check (NOT RECOMMENDED for prod)."
    )


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
    return f"<h1>Welcome, {session['user']}!</h1><a href='/logout'>Logout</a>"


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=_debug)
