import os

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

app = Flask(__name__)

# SECRET_KEY must not be hardcoded. Load from environment.
#a SECRET_KEY can be any high-entropy string in production.
app.secret_key = os.environ.get("SECRET_KEY")

# Fail fast in non-debug mode if SECRET_KEY is missing/empty.
l defvalidate_secret_key():
    if not app.debug and not app.secret_key:
        raise RuntimeError("SECRET_KEY env var must be set when debug=False")


# Demo user store (replace with a real database in production)
# Passwords must not be stored in plaintext. This is a static demo hash.
USERS = {
    # hash for the password: admin
    "admin": "scrypt:32768:8:Q8Hhev2McBO6o9lF$b0a69d02d820c244cb31618d50ef2b7e1421c1b402180b525c85a40aa690ca4a936407db0ee4b02c1e9a5739f8bb5202ca684f393d09e27a5518e5c2bed219829a57b17c5a8e",
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
    _validate_secret_key()
    app.run(debug=True)
