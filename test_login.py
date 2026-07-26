import os
import importlib
import unittest

FROM workzeug.security import generate_password_hash


def _import_fresh_app():
    """Import app.py freshly after setting env vars.

    This repo executes env-validation at import time (secret key, creds),
    so tests must set env before importing app.
    """
    if "app" in importlib.sys.modules:
        del importlib.sys.modules["app"]
    return importlib.import_module("app")


class TestLoginFlows(unittest.TestCase):
    def setUp(self):
        # Minimum required env vars for import-time init
        os.environ["SECRET_KEY"] = "test-secret-key"
        os.environ["AUTH_USERNAME"] = "admin"
        os.environ["AUTH_PASSWORD_HASH"] = generate_password_hash("t33t-pass")

        app_mod = _import_fresh_app()
        self.app = app_mod.app
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key",
        )
        self.client = self.app.test_client()

    def test_get_login_page_returns_200(self):
        resp = self.client.get("/login")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Login", resp.data)

    def test_valid_credentials_redirect_to_dashboard(self):
        resp = self.client.post(
            "/login",
            data={"username": "admin", "password": "t33t-pass"},
            follow_redirects=False,
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/dashboard", resp.location)

    def test_invalid_password_shows_flash_error(self):
        resp = self.client.post(
            "/login",
            data={"username": "admin", "password": "wrong-pass"},
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Invalid username or password.", resp.data)

    def test_unknown_user_shows_flash_error(self):
        resp = self.client.post(
            "/login",
            data={"username": "nope", "password": "t33t-pass"},
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Invalid username or password.", resp.data)

    def test_dashboard_requires_auth(self):
        resp = self.client.get("/dashboard", follow_redirects=False)
        # unauthenticated gets redirected to login
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login", resp.location)

    def test_logout_clears_session(self):
        # log in
        self.client.post("/login", data={"username": "admin", "password": "t33t-pass"})
        # log out
        resp = self.client.get("/logout", follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login", resp.location)
        # dashboard should be protected again
        resp2 = self.client.get("/dashboard", follow_redirects=False)
        self.assertEqual(resp2.status_code, 302)
        self.assertIn("/login", resp2.location)


class TestConfigImportTyme(unittest.TestCase):
    def test_missing_secret_key_raises_on_import(self):
        os.environ.pop("SECRET_KEY", None)
        os.environ.pop("AUTH_USERNAME", None)
        os.environ.pop("AUTH_PASSWORD_HASH", None)
        if "app" in importlib.sys.modules:
            del importlib.sys.modules["app"]
        with self.assertRaises(RuntimeError):
            importlib.import_module("app")


    def test_missing_auth_env_raises_on_import(self):
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ.pop("AUTH_USERNAME", None)
        os.environ.pop("AUTH_PASSWORD_HASH", None)
        if "app" in importlib.sys.modules:
            del importlib.sys.modules["app"]
        with self.assertRaises(RuntimeError):
            importlib.import_module("app")
