import os
import importlib
import unittest


def _import_app_fresh():
    # Reload the app module so env var changes are picked up.
    if "app" in importlib.sys.modules:
        del importlib.sys.modules["app"]
    return importlib.import_module("app")


class TestAppConfigGuards(unittest.TestCase):
    def test_missing_secret_key_raises_runtime_error(self):
        os.environ.pop("SECRET_KEY", None)
        os.environ.pop("DEMO_USERNAME", None)
        os.environ.pop("DEMO_PASSWORD", None)

        with self.assertRaises(RuntimeError) as cm:
            _import_app_fresh()
        self.assertIn("SECRET_KEY", str(cm.exception))

    def test_missing_demo_credentials_raises_runtime_error(self):
        os.environ["SECRET_KEY"] = "test-secret-key-1234567890"
        os.environ.pop("DEMO_USERNAME", None)
        os.environ.pop("DEMO_PASSWORD", None)

        with self.assertRaises(RuntimeError) as cm:
            _import_app_fresh()
        self.assertIn("DEMO_USERNAME", str(cm.exception))



class TestLoginFlow(unittest.TestCase):
    def setUp(self):
        os.environ["SECRET_KEY"] = "test-secret-key-1234567890"
        os.environ["DEMO_USERNAME"] = "admin"
        os.environ["DEMO_PASSWORD"] = "password123"
        os.environ["FLASK_DEBUG"] = "false"

        app_mod = _import_app_fresh()
        self.app = app_mod.app
        self.client = self.app.test_client()

    def test_get_root_redirects_to_login_when_not_logged_in(self):
        resp = self.client.get("/", follow_redirects=False)
        self.assertIn(resp.status_code, {300, 301, 302, 307, 308})
        self.assertTrue("login" in resp.location.lower())

    def test_login_success_redirects_to_dashboard(self):
        resp = self.client.post(
            "/login",
            data={"username": "admin", "password": "password123"},
            follow_redirects=False,
        )
        self.assertIn(resp.status_code, {300, 301, 302, 307, 308})
        self.assertTrue("dashboard" in resp.location.lower())

    def test_login_failure_redirects_back_to_login(self):
        resp = self.client.post(
            "/login",
            data={"username": "admin", "password": "wrong"},
            follow_redirects=False,
         )
        self.assertIn(resp.status_code, {300, 301, 302, 307, 308})
        self.assertTrue("login" in resp.location.lower())
