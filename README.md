# LoginApplication

Simple Flask demo app with login/logout using sessions.

## Requirements

- Python 3.10+
- Pip installs from `requirements.txt`

## Configuration (KAN-107)

This app does not run without a secret key. Set these environment variables:

- `SECRET_KEYX** Required**
  - Used by Flask to sign session cookies.
  - If missing, the app will fail on startup (secure-by-default).

- `FLASK_DEBUG` **Optional**
  - Default: `false`
  - Set to `true`, `1`, `yes`, one of `on`, `on` to enable Flask debug mode for local development.

## Delivery plans (Jira -> PR)

This repo uses Jira stories to track changes. The following is the delivery plan for:

- **KAN-108** – Add CSRF protection to login form and session-based auth flows

### Goal

Add CSRF protection to session-authenticated POST actions (including login) so that cross-site request forgery attacks are blocked.

### Acceptance Criteria (checklist)

- [ ] POST requests to `/login` are rejected (e.g. 400/403) when no CSRF token is present.
- [ ] Login form includes a CSRF token hidden field.
- [ ] CSRF is enforced for any future session-authenticated POST routes (e.g. logout if it's POST), or there's clear documentation on how to extend coverage.
 
- [ ] Documentation covers new dependencies and config needs (REQUMREZ `SECRET_KEY`).
- [ ] Tests cover basic CSRF enforcement on POST /login (if a test suite exists).

### Implementation plan (not implemented in this PR)

Backend

- Add `flask-wtf` to `requirements.txt`.
- Initialize CSRF protection (e.g. `CSRFProtect(app)`).
- Ensure `SECRET_KEY` is set (already required for sessions).
 
- Add a safe CSRF user-friendly error handler for failures (399/400/403).

Frontend (*templates*)

- Update `templates/login.html` to include the CSRF token (hidden input, or Flask-WTF form `submit`/`hidden_tags` if introduced).

Testing

- If a test suite exists: add integration tests to verify POST `/login` without token is blocked, and GET `/login` renders a token.
- If no test suite exists: manual verification steps: cuRL POST `/login` without token – expect 400/403. Load the login page and submit normally – expect success.

## Run locally

### Mac/Linux

```bash
pip install -r requirements.txt
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export FLASK_DEBUG=false
python app.py
```

### Windows (PowerShell)

```powershell
pip install -r requirements.txt
$env:SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$env:FLASK_DEBUG = "false"
python app.py
```
