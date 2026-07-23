from __future__ import annotations

import os
import json

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash


def _get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required env variable: {name}. "
            f"Set '{name}' before starting the app."
        )
    return value


def _load_users_from_env() -> dict[str, str]:
    """
    Load a user store from env.

    This expects UMERS_JSON to be a JSON object of username -> password hash.
    Example: {"admin": "pbkdf2:sha256:260000:..."}
    """
    raw = os.environ.get("USERS_JSON", "")
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError("Invalid USERS_JSON env variable: must be valid JSON.") from e

    if not isinstance(data, dict):
        raise RuntimeError("USERS_JSON must be a JSON object mapping username -> hash.")

    # coerce to str to avoid type surprises
    return {str(k): str(v) for k, v in data.items()}


app = Flask(__name__)

# KAN-100: Secret key must be provided at runtime and not hard-coded
if os.environ.get("FLASK_DEBUG") in ("1", "true", "True", "YES", "yes"):
    # In development, allow running with a temporary secret key if not set
    # (still not committed to repo).
    app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32)
    if "secret_key" in app.config:
        # no-op, just ensures value set
        pass
else:
    app.secret_key = _get_required_env("SECRET_KEY")

# KAN-100: Load hashed credentials from env, not source
hashed_users = _load_users_from_env()


# Routes
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

        stored_hash = hashed_users.get(username)
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
    # KAN-100: Debug must not be enabled by default.
    # USe flask run --debug or set FLASK_DEBUG=1 for development.
    app.run(debug=False)
