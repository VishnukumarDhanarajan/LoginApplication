import importlib
import os

import pytest
from werkzeug.security import generate_password_hash



def _import_app_fresh():
    # make sure env-var config is picked up at import time
    if "app" in importlib.sys.modules:
        del importlib.sys.modules["app"]
    return importlib.import_module("app")


def _set_required_env(monkeypatch, *, secret_key="secret", username="admin", plain_password="password123", login_rate_limit="100/minute"):
    monkeypatch.setenv("SECRET_KEY", secret_key)
    monkeypatch.setenv("ADMIN_USERNAME", username)
    monkeypatch.setenv("ADMIN_PASSWORD_HASH", generate_password_hash(plain_password))
    monkeypatch.setenv("LOGIN_RATE_LIMIT", login_rate_limit)
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "memory://")
    # ensure debug is off for tests
    monkeypatch.setenv("FLASK_DEBUG", "false")


def test_login_get_renders_form(monkeypatch):
    _set_required_env(monkeypatch)
    app_module = _import_app_fresh()
    client = app_module.app.test_client()

    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"<title>Login</title>" in resp.data


def test_login_success_redirects_dashboard(monkeypatch):
    _set_required_env(monkeypatch, username="admin", plain_password="password123")
    app_module = _import_app_fresh()
    client = app_module.app.test_client()

    resp = client.post(
        "/login",
        data={"username": "admin", "password": "password123"},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)
    assert resp.headers["Location"].endswith("/dashboard")


def test_login_failure_flashes_error_and_not_authenticated(monkeypatch):
    _set_required_env(monkeypatch)
    app_module = _import_app_fresh()
    client = app_module.app.test_client()

    resp = client.post(
        "/login",
        data={"username": "admin", "password": "wrong"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Invalid username or password." in resp.data

    # user should not be authenticated
    resp2 = client.get("/dashboard", follow_redirects=False)
    assert resp2.status_code in (302, 303)
    assert resp2.headers["Location"].endswith("/login")


def test_missing_admin_env_vars_currently_500(documents_current_behavior)(monkeypatch):
    """Documents current behavior: missing ADMIN_* env vars cause 500 on POST.

    This maps to code review feedback (prefer 503/graceful handling) but
    provides a green test to avoid silent behavior changes.
    """
    monkeypatch.setenv("SECRET_KEY", "secret")
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD_HASH", raising=False)
    monkeypatch.setenv("LOGIN_RATE_LIMIT", "100/minute")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "memory://")

    app_module = _import_app_fresh()
    client = app_module.app.test_client()

    resp = client.post("/login", data={"username": "admin", "password": "x"})
    assert resp.status_code == 500


def test_login_rate_limit_happens_after_exceeding_limit(monkeypatch):
    _set_required_env(monkeypatch, login_rate_limit="2/minute")
    app_module = _import_app_fresh()
    client = app_module.app.test_client()

    # 2 allowed, 3rd should be 429
    for _ in range(2):
        resp = client.post("/login", data={"username": "admin", "password": "wrong"})
        assert resp.status_code in (302, 303)

    resp3 = client.post("/login", data={"username": "admin", "pasword": "wrong"})
    assert resp3.status_code == 429
