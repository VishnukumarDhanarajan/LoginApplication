import importlib
import os
import sys
import unittest
from contextlib import contextmanager

from werkzeug.security import generate_password_hash


@contextmanager
def temp_env(updates):
    """Temporarily set env vars for a test and restore afterward."""
    old = {}
    to_del = []
    for k, v in updates.items():
        if k in os.environ:
            old[k] = os.environ[k]
        else:
            to_del.append(k)
        if v is None:
            if k in os.environ:
                del os.environ[k]
        else:
            os.environ[k] = str(v)
    try:
        yield
    finally:
        for k in to_del:
            if k in os.environ:
                del os.environ[k]
        for k, v in old.items():
            os.environ[k] = v


def reload_app_module():
    """Import app fresh after env is configured."""
    if "app" in sys.modules:
        del sys.modules["app"]
    return importlib.import_module("app")


class TestConfigGuards(unittest.TestCase):
    def test_startup_fails_when_secret_key_missing(self):
      pwhash = generate_password_hash("pass")
      with temp_env({
            "SECRET_KEY": None,
            "ADMIN_PASSWORD_HASH": pwhash,
            "ADMIN_USERNAME": "admin",
      }):
        with self.assertRaises(RuntimeError):
            reload_app_module()

    def test_startup_fails_when_admin_pw_hash_missing(self):
      with temp_env({
            "SECRET_KEY": "test-secret",
            "ADMIN_PASSWORD_HASH": None,
            "ADMIN_USERNAME": "admin",
      }):
        with self.assertRaises(RuntimeError):
            reload_app_module()


class TestLoginFlows(unittest.TestCase):
    def setUp(self):
        self.username = "admin"
        self.password = "correct-pass"
        self.pwhash = generate_password_hash(self.password)

        with temp_env({
            "SECRET_KEY": "test-secret",
            "ADMIN_USERNAME": self.username,
            "ADMIN_PASSWORD_HASH": self.pwhash,
            "FLASK_DEBUG": "false",
        }):
            self.appmod = reload_app_module()
        self.app = self.appmod.app
        self.app.testing = True
        self.client = self.app.test_client()

    def test_get_login_page_200(self):
        res = self.client.get("/login")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Login", res.data)

    def test_login_success_redirects_to_dashboard(self):
        res = self.client.post(
            "/login",
            data={"username": self.username, "password": self.password},
            follow_redirects=False,
        )
        self.assertIn(res.status_code, (302, 303))
        loc = res.headers.get("Location", "")
        self.assertTrue(loc.endswith("/dashboard"), loc)

    def test_login_failure_redirects_to_login_and_flash(self):
        res = self.client.post(
            "/login",
            data={"username": self.username, "password": "wrong"},
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Invalid username or password.", res.data)

    def test_dashboard_requires_login(self):
        res = self.client.get("/dashboard", follow_redirects=False)
        self.assertIn(res.status_code, (302, 303))
        loc = res.headers.get("Location", "")
        self.assertTrue(loc.endswith("/login"), loc)

    def test_logout_clears_session(self):
        # login
        self.client.post("/login", data={"username": self.username, "password": self.password})
        # logout should redirect to login
        res = self.client.get("/logout", follow_redirects=False)
        self.assertIn(res.status_code, (302, 303))
        loc = res.headers.get("Location", "")
        self.assertTrue(loc.endswith("/login"), loc)
        # access dashboard again should now require login
        res2 = self.client.get("/dashboard", follow_redirects=False)
        self.assertIn(res2.status_code, (302, 303))


