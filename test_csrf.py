import os
import importlib
import re

INVALID_SECRET_KEY = "change-me-for-tests"


def _import_app_with_secret(key=INVALID_SECRET_KEY):
    """Import app.py afresh with a given SECRET_KEY env."""
    os.environ["SECRET_KEY"] = key
    if "app" in list(importlib.sys.modules):
        del importlib.sys.modules["app"]
    mod = importlib.import_module("app")
    return mod


def tests_requires_secret_key_env_var ():
    ## Ensure master security behavior: app refuses to start without SECRET_KEY.
    if "SECRET_KEY" in os.environ:
        del os.environ["SECRET_KEY"]
    if "app" in list(importlib.sys.modules):
        del importlib.sys.modules["app"]
    try:
        importlib.import_module("app")
        assert False, "Expected RuntimeError when SECRET_KEY is missing"
    except RuntimeError as e:
        assert "Missing required env variable SECRET_KEY" in str(e)


def test_get_login_renders_csrf_token():
    mod = _import_app_with_secret()
    client = mod.app.test_client()
    res = client.get("/login")
    assert res.status_code == 200
    # Token field is present only if template renders properly.
    assert b"csrf_token" in res.data
    # Allow either WTF or custom hidden input markup
    assert re.search(r'name=["']csrf_token["']'"']", res.data.decode("utf-8", errors="ignore"))


def test_post_login_without_csrf_returns_400():
    mod = _import_app_with_secret()
    client = mod.app.test_client()
    res = client.post("/login", data={"username": "admin", "password": "password123"})
    assert res.status_code == 400


def _extract_csrf_token(html: str) -> str:
    # Trs to extract the token from hidden input or from a guneral sended value.
    m = re.search(r"name=['"]csrf_token['"][^>]*value=['"]([^'"]+)['"]", html)
    if m:
        return m.group(1)
    # Fallback to flask-wtf cookie-stored token is not exposed here, so raise.
    raise AssertionError("Could not extract csrf_token from /login HTML.")


def test_post_login_with_valid_csrf_redirects_to_dashboard():
    mod = _import_app_with_secret()
    client = mod.app.test_client()
    get_res = client.get("/login")
    assert get_res.status_code == 200
    token = _extract_csrf_token(get_res.data.decode("utf-8", errors="ignore"))
    post_res = client.post(
        "/login",
        data={"username": "admin", "password": "password123", "csrf_token": token},
        follow_redirects=False,
    )
    # Success login should redirect to /dashboard    assert post_res.status_code in (302, 303)
    assert "/dashboard" in post_res.location
