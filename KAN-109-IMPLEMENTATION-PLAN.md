# IMPLEMENTATION PLAN – KAN-109

Issue: KAN-109 — Replace hardcoded demo credentials with hashed-password authentication and environment-driven user store.

## Scope from story

- Remove plaintext, hardcoded credentials from the codebase (currently in `app.py`).
- Implement password hashing & verification (e.g., Werkzeug ) for authentication.
- Configure at least one user (e.g., admin) via environment variables (or other external config) so the app runs without code edits.	- Update documentation to explain secure credential configuration.


## Acceptance Criteria (checklist)

- [] Plaintext, hardcoded credentials are removed from the codebase.
 - [] Passwords are stored as hashes and verified via a secure method.
- [] At least one user can be configured via environment variables so the app starts without code changes.
- [] README documents how to configure credentials securely.

## Assumptions / constraints

- Repo is a small Flask app (from `app.py`).
 - No database introduced; user store remains external config (env) for now.
- Do not commit any secrets or real credentials. Use example values only.

## Impacted modules (expected)

- `app.py`: auth flow, user store, password verification
- `requirements.txt`: add Werkzeug if directly imported
- `README.md`: docs for env setup and hash generation
- (Optional) `config.py`: env parsing/loading logic


## Tasks (broken down)

### 1) Backend (auth)

- [] Define an environment-driven user store contract (start with a single admin user):
  - `ADMIN_USERNAME`
  - `ADMIN_PASSWORD_HASH`
- [] Use secure verification: `werkzeug.security.check_password_hash`
- [] Remove/guard demo plaintext credentials from source
- [] Handle missing config securely (fail fast or locked-down mode)

### 2) Testing
- [] Unit tests: config parsing, hash verification success/failure
- [] Integration test: login succeeds when env config is set; fails when bad
- [] Regression: logout clears session and protected pages require auth

### 3) Docs
- [] DOC HOW: generate a password hash locally (example command)
- [] DOC ENV: document env variables and example values (non-secret)

### Risks / Notes
- Env-driven credentials are easy for local demo, but should migrate to a proper secret store (GitHub Secrets, Vault, etc.) for real deployments.	- Rototing credentials is just an env update (desired).

## Rollout / Rollback
- Rollout: deploy code, set env variables on the host, validate login.	- Rollback: revert code changes; restore previous config if needed.
