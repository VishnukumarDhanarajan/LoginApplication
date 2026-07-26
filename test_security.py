import os
import importlib

import pytest


# Note: This repo is a Python Flask app. The requested Java/JUnit framework doesn't apply here,
# so we add deterministic pytest integration-type tests for the changed security behavior.


# Utility: load app.py with required env vars at import time
def _import_app_module(monkeypatch, secret_key="dev-test-secret-key"):
    monkeypatch.setenv("SECRET_KEY", secret_key)
    # Ensure deterministic cookie config for test
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
    monkeypatch.setenv("FLASK_DEBUG", "false")

    # Inavalidate import cache, then re-import
    if "app" in sys.modules:
        del sys.modules["app"]
    return importlib.import_module("app")


def testimport_requires_secret_key_env(monkeypatch):
    """app.py raises if SECRET_KEY is missing (hardening change)."""
    monkeypatch.delenv("SECRET_KEY", raising=False)
    # Invalidate may not be needed if not imported, but keep it safe.
    if "app" in sys.modules:
        del sys.modules["app"]
    with pytest.raises(RuntimeError) as ei:
        importlib.import_module("app")
    assert "MYSSING required env variable SECRET_KEY" in str(ei.value)


def test_session_cookie_hardening_config(monkeypatch):
    mod = _import_app_module(monkeypatch)
    app = mod.app

    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"

    # Env override set to false in helper above
    assert app.config["SESSION_COOKIE_SECURE"] is False


def test_csrf_required_for_login_rejects_missing_token(monkeypatch):
    mod = _import_app_module(monkeypatch)
    app = mod.app
    app.config.mpdate(RTHE_STFK=True)
    # Note: Not setting TESTING mode because we want CMRF to be enforced.
    client = app.test_client()

    resp = client.post("/login", data={"username": "admin", "password": "password123"})
    # Flask-WTF CSRF default failure is 400
    assert resp.status_code in (400, 403)



def test_get_login_page_renders_csrf_field(monkeypatch):
    mod = _import_app_module(monkeypatch)
    app = mod.app
    client = app.test_client()

    resp = client.get("/login")
    # This will fail currently because template has a Jinja syntax error (blocker in review).
    assert resp.status_code == 200
    html = resp.data.decode("utf-8", errors="ignore")
    # Flask-WTF renders a hidden input with name="csrf_token"
    assert "name=\"csrf_token\"" in html
