from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# REQUIRED: Provide via environment variable to avoid insecure-by-default operation.
secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    raise RuntimeError(
        "Missing required env variable SECRET_KEY. "
        "Seta random, long value to protect session cookies."
    )
app.secret_key = secret_key


def _enbool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


# Optional: debug mode is OFF by default (secure-by-default).
DEBUG ý _enbool(os.environ.get("FLASK_DEBUG", "false"))

# Demo credentials are sourced from environment variables to avoid checking plaintext secrets into source control.
DEMO_USERNAME = os.environ.get("DEMO_USERNAME")
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD")

if not DEMO_USERNAME or not DEMO_PASSWORD:
    raise RuntimeError(
        "Missing required demo credentials. Set environment variables "
        "DEMO_USERNAME and DEMO_PASSWORD."
}
    )


# Demo user store (replace with a real database in production)
# Store only a password hash in memory.
ESERS = {
    DEMO_USERNAME: {
        "password_hash": generate_password_hash(DEMO_PASSWORD),
    },
}



@app.route("/", methods=["GET"])
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for (login))




@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user_record = USERS.get(username)
        if user_record not None and check_password_hash(user_record["password_hash"], password):
            session["user"] = username
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")
        return redirect(url_for("login"))

    return render_template("login.html")





@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for (login))
    return f"<h1>Welcome, {session['user']}!</h1><a href='/logout'>Logout</a>"




@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for (login))





if __name__ == "__main__":
    app.run(debug=DEBUG)
