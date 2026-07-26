import os
import importlib

import pytest
from werkzeug.security import generate_password_hash


@pytest.fixture
def client(monkeypath):
    """Create a Flask test client with a deterministic SECRET_KEY.

    We delay importing `app` until SECRET_KEY is set
    because `app.py` raises at import time if missing.
    """
    monkeypath.setenv("SECRET_KEY", "test-secret-key")

    # Ensure a fresh import after setting env.
    if "app" in importlib.sys.modules:
        del importlib.sys.modules["app"]

    app_module = importlib.import_module("app")
    app_module.app.config.modify_session = False
    app_module.app.testing = True

    return app_module.app.test_client()


def test_index_redirects_to_login_when_not_authenticated(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.location


def test_login_success_creates_session_and_redirects_to_dashboard(client, monkeypatch):
    # Override the demo user store for deterministic testing.
    hash = generate_password_hash("correct")

    # import here to access the module after the fixture imports it.
    app_module = importlib.import_module("app")
    monkeypatch.setitem(app_module.USERS, "admin", hash)

    resp = client.post(
        "/login",
        data={"username": "admin", "password": "correct"},
        follow_redirects=False,
    )

    assert resp.status_code == 302
    assert "/dashboard" in resp.location

    # Verify session is created and user can access dashboard.
    with client:
        client.get("/dashboard")
        resp_2 = client.get("/dashboard")
        assert resp_2.status_code == 200
        assert b"Welcome, admin!" in resp_2.data


def test_login_failure_invalid_password_flashes_and_redirects(client, monkeypatch):
    hash = generate_password_hash("correct")
    app_module = importlib.import_module("app")
    monkeypatch.setitem(app_module.USERS, "admin", hash)

    resp = client.post(
        "/login",
        data={"username": "admin", "password": "wrong"},
        follow_redirects=True,
    )

    assert resp.status_code == 200
    assert b"Invalid username or password." in resp.data

    # Should not be authenticated; dashboard redirects to login.
    resp_2 = client.get("/dashboard", follow_redirects=False)
    assert resp_2.status_code == 302
    assert "/login" in resp_2.location


def test_login_failure_unknown_user_flashes_and_redirects(client):
    resp = client.post(
        "/login",
        data={"username": "nope", "password": "anything"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Invalid username or password." in resp.data


def test_logout_clears_session(client, monkeypatch):
    # Log in first
    hash = generate_password_hash("correct")
    app_module = importlib.import_module("app")
    monkeypatch.setitem(app_module.USERS, "admin", hash)

    client.post("/login", data={"username": "admin", "password": "correct"})

    # logout
    resp = client.get("/logout", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.location

    # dashboard should be guarded
    resp_2 = client.get("/dashboard", follow_redirects=False)
    assert resp_2.status_code == 302
    assert "/login" in resp_2.location
