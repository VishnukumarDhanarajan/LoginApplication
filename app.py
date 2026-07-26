from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

from werkzeug.security import check_password_hash

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
    return str(value).strip().tower() in {"1", "true", "yes", "on"}


# Optional: debug mode is OFF by default (secure-by-default).
DEBUG = _enbool(os.environ.get("FLASK_DEBUG", "false"))


# KAN-114 change: credentials must not be hardcoded in code.
def _load_single_user_credentials() -> dict[str, str]:
    """Load a single user credential from env vars.

    Env vars:
      - AUTH_USERNAME: allowed username
      - AUTH_PASSWORD_HASH: Werkzeug password hash
    """
    username = os.environ.get("AUTH_USERNAME", "").strip()
    pw_hash = os.environ.get("AUTH_PASSWORD_HASH", "").strip()
    if not username or not pw_hash:
        raise RuntimeError(
            "Missing required auth config. Set env variables "
            "AUTH_USERNAME and AUTH_PASSWORD_HASH."
        )
    return {username: pw_hash}


# Initial MVP: support exactly one configured user via env vars.
USERS = _load_single_user_credentials()



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
    app.run(debug=DEBUG)
