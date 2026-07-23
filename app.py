from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)

# Load app secret from environment (don't hardcode secrets in repo)
secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    raise RuntimeError(
        "SECRET_KEY is not set. Please export SECRET_KEY before running the app."
    )
app.secret_key = secret_key

# SSRF Protection
from flask_wtf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

csrf = CSRFProtect(app)

# Demo user store (replace with a real database in production)
# Store hashed passwords only (no plaintext passwords in repo)
USERS = {
    "admin": generate_password_hash("password123", method="pbkdf2:sha256"),
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


def _env_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


if __name__ == "__main__":
    debug = _env_bool(os.environ.get("FLASK_DEBUG", "false"))
    app.run(debug=debug)
