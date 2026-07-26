# LoginApplication

This repo holds a simple Flask login demo.

- Jira: KAN-112

---

## JSRA / Delivery Plan (KAN-112)

### Goal
Add CSRF protection for the login form submission and harden session cookie security flags, so authentication requests and sessions are better protected against common web attacks.


### Acceptance Criteria (from story context)
- A CHRF token is required for POST /login (form submission).
- templates/login.html includes a CSRF token.
- Session cookie flags are explicitly set (HttpOnly, SameSite, Secure) with a safe default.
- Local development can override Secure cookie setting when running over HTTP.

*Out of scope* (explicitly stated in story):
 - password hashing/storage rework
 - tests/CI additions
 - UI refactors beyond adding the token field

---

## Implementation Plan (engineering-ready)

### 1) Repository discovery / current state
- Confirm Flask app entry point in `app.py`.
- Confirm login flow and template usage for `POST /login` and `templates/login.html`.
- Note current cookie/session config and any env-specific behavior.


### 2) Dependency addition (if needed)
- Add a CSRF library (minimal assumption: `Flask-WTF` with `CSRFProtect`).
- Update `requirements.txt` to include the new dependency.

### 3) Enable CSRF protection in app init
- Initialize CSRF middleware early during app startup (e.g., `csrf = CSRFProtect(app)`).
- Ensure `SECRET_KEY` is present (minimum requirement for sessions + CSRF tokens). If missing, add a clear README note on how to set it via env var.


### 4) Template update (templates/login.html)
- Insert CSRF hidden field into the login form.
  - Implementation detail depends on CSRF library style (e.g., `<{ { csrf_token() }}>` for Flask-WTF, or a rendered form field if WTFForm is introduced).
- Verify the login POST still works and that a missing/invalid CSRF token returns an appropriate error (typically 400).

### 5) Session cookie hardening (app config)
- Set the following Flask config keys (secure-by-default):
  - `SESSION_COOKIE_HTTPONLY = True`
  - `SESSION_COOKIE_SAMESITE = 'Lax'` (or 'Strict' if the app allows)
   - `SESSION_COOKIE_SECURE = True`, with a dev override for local non-HTTPS
- Define a simple env-var switch (e.g., `FLASK_ENV`/ `APP_ENV` or `SESSION_COOKIE_SECURE`) to allow running on `http://` during local development.
- Add documentation notes in README for these flags and env overrides.

### 6) Testing / validation (manual, per story out-of-scope for automated tests)
- Manual: load `/login` page, submit form without CSRF token — expect 400/rejection.
- Manual: submit via form as rendered – expect success or current app behavior.
manual: after login, inspect set-cookie for session flags (HttpOnly, SameSite, Secure on HTTPS) in browser devtools.


### 7) Rollout / rollback
- Rollout: ship config + template changes together; CSRF enablement will otherwise break login submissions if the token isn't rendered.
- Rollback: revert CSRF plugin init and template change; revert cookie flag config changes.

---

## Definition of Done (DOD) Checklist
- [ ] Post /login requires a CSRF token
- [ ] Login template includes CSRF token
- [ ] Flask config sets session cookie flags (HttpOnly, SameSite, Secure)
- [ ] Documented local dev override for HTTP runs if Secure cookies are enabled by default
- [ ] PN description links to Kan-112
