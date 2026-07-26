from __future__ import annotations

import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

# Throttling
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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


def _get_env_credential_pair() -> tuple[str | None, str | None]:
    """Return (username, password_hash) from environment.

    Contract per Confluence page:
      - ADMIN_USERNAME: string
      - ADMIN_PASSWORD_HASH: string (Werkzeug generate_password_hash output)

    No plaintext password is accepted to avoid reintroducing secrets into env.
    """

    return (
        os.environ.get("ADMIN_USERNAME"),
        os.environ.get("ADMIN_PASSWORD_HASH"),
    )


# Optional: debug mode is OFF by default (secure-by-default).
DEBUG = _enbool(os.environ.get("FLASK_DEBUG", "false"))

# Throttling policy
# Default: 5 requests/minute per IP for /login POSTs.
# Configure via LOGIN_RATE_LIMIT (e.g., "10/minute").
LOGIN_RATE_LIMIT = os.environ.get("LOGIN_RATE_LIMIT", "5/minute")

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    # Keep in-memory storage (demo/single instance). Confluence notes that
    # multi-instance/shared store is out of scope.
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
)


@app.route("/", methods=["GET"])
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
@limiter.limit(LOGIN_RATE_LIMIT)
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin_username, admin_password_hash = _get_env_credential_pair()

        if not admin_username or not admin_password_hash:
            # Fail closed: do not allow login without configured creds.
            raise RuntimeError(
                "Missing ADMIN_USERNAME / ADMIN_PASSWORD_HASH environment variables. "
                "Configure a hashed password per README."  # README update lives in PR #20.
            )

        if username == admin_username and check_password_hash(admin_password_hash, password):
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
