import importlib

import os
import sys
import pytest


def _load_app_module(monkeypatch):
    """Loads app.py freshly after applying env variables.

    App init code runs at import time, so this helper
    explicitly evicts the module from sys.modules before re-import.
    """
    if "app" in sys.modules:
        del sys.modules["app"]
    return importlib.import_module("app")


@pytest.mark.parametrize(
    "value,expected",
    [
        ("true", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("false", False),
        ("0", False),
        ("no", False),
        ("off", False),
        ("", False),
        ("  true  ", True),
    ],
)
def test_env_boolean_parsing_for_session_cookie_secure(monkeypatch, value, expected):
    """Covers: app.config["SESSION_COOKIE_SECURE"] parsing logic."""
    monkeypatch.setenv("FLASK_DEBUG", "true")  # bypass SECRET_KEY requirement for this test
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("SESSION_COOKIE_SECURE", value)

    app_module = _load_app_module(monkeypatch)
    assert app_module.app.config["SESSION_COOKIE_SECURE"] is expected



def test_missing_secret_key_raises_in_non_debug(monkeypatch):
    """Covers: fail-fast behavior when FLASK_DEBUG=false and SECRET_KEY missing."""
    monkeypatch.setenv("FLASK_DEBUG", "false")
    monkeypatch.delenv("SECRET_KEY", raising=False)

    if "app" in sys.modules:
        del sys.modules["app"]

    with pytest.raises(RuntimeError) as exc:
        importlib.import_module("app")

    assert "Missing required env var: SECRET_KEY" in str(exc.value)



def test_missing_secret_key_allowed_in_debug(monkeypatch):
    """Covers: bypass behavior when FLASK_DEBUG=$true."""
    monkeypatch.setenv("FLASK_DEBUG", "true")
    monkeypatch.delenv("SECRET_KEY", raising=False)

    app_module = _load_app_module(monkeypatch)
    assert app_module._debug is True
    # SECRET_KEY may be None in this mode per current implementation
    assert app_module.app.config.get("SECRET_KEY") is None



def test_cookie_defaults(monkeypatch):
    """Covers defaults: HttpOnly True, SameSite Lax, Secure True."""
    monkeypatch.setenv("FLASK_DEBUG", "true")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("SESSION_COOKIE_SAMESITE", raising=False)
    monkeypatch.delenv("SESSION_COOKIE_SECURE", raising=False)

    app_module = _load_app_module(monkeypatch)
    assert app_module.app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app_module.app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app_module.app.config["SESSION_COOKIE_SECURE"] is True



def test_login_success_sets_session_and_redirects(monkeypatch):
    """Integration-ish test using Flask test client."""
    monkeypatch.setenv("FLASK_DEBUG", "true")
    monkeypatch.delenv("SECRET_KEY", raising=False)

    app_module = _load_app_module(monkeypatch)
    client = app_module.app.test_client()

    resp = client.post(
        "/login",
        data={"username": "admin", "password": "password123"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/dashboard" in resp.headers.get("Location", "")

    # Session cookie should be set on successful login
    set_cookie = resp.headers.get("Set-Cookie", "")
    assert "session=" in set_cookie



def test_login_failure_flashes_and_redirects(monkeypatch):
    """Covers invalid credentials path."""
    monkeypatch.setenv("FLASK_DEBUG", "true")
    monkeypatch.delenv("SECRET_KEY", raising=False)

    app_module = _load_app_module(monkeypatch)
    client = app_module.app.test_client()

    resp = client.post(
        "/login",
        data={"username": "admin", "password": "wrong"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/login" in resp.headers.get("Location", "")

    # Follow redirect to see flashed message rendered
    page = client.get("/login")
    assert page.status_code == 200
    assert b"Invalid username or password" in page.data


def test_dashboard_requires_auth_redirects_to_login(monkeypatch):
    """Covers guard clause in /dashboard."""
    monkeypatch.setenv("FLASK_DEBUG", "true")
    monkeypatch.delenv("SECRET_KEY", raising=False)

    app_module = _load_app_module(monkeypatch)
    client = app_module.app.test_client()

    resp = client.get("/dashboard", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers.get("Location", "")
