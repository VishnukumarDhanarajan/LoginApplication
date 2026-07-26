# LoginApplication

This is a small Flask demo app with login/logout.

## Jira

- KAN-113: Replace hardcoded login credentials with hashed-password authentication and brute-force throttling

## Implementation Plan (KAN-113)

> Note: This PR only adds this plan and documentation. It does not implement the auth changes yet.


### Goals
1. Remove plaintext credentials from source code (no committed secrets)
2. Support password hashing using Werkzeug helpers (`generate_password_hash`, `check_password_hash`)
3. Add minimal brute-force throttling (rate limiting or cooldown/lockout)

### Acceptance Criteria (checklist)
- [ ] No plaintext passwords remain in `app.py` or other tracked files
- [ ] Login flow uses hash verification (raw string equals check is removed)
- [ ] Demo credentials are supplied via environment variables (or a local dev file that is gitignored)
- [ ] Failed login attempts are throttled (e.g. per-IP or per-session)
- [ ] Behavior is documented (local dev, testing, and config knobs)


### Design / Technical Approach

#### 1) Password hashing
* Use Werkzeug security helpers:
  - `from werkzeug.security import generate_password_hash, check_password_hash`
* Replace `USERS` values from plaintext to hashes.
* Update login check from:
  - `USERS.get(username) == password`
  to:
  - `if stored_hash and check_password_hash(stored_hash, password):`

#### 2) Move demo credentials out of source
Options (ordered by simplicity for a demo):

1. **Env-var backed* (pilot)
  - `with echo $ADMIN_USERNAME / $ADMIN_PASSWORD_HASH``
  - Add notes in README with example usage
   * Note: never commit real values to git
2. **Local dev file** (gitignored)
  - e.g. `.env or `credentials.json`
  - Add a sample template file ending in `.example`

#### 3) Throttling /brte-force mitigation
* Minimal approach options:
  - **Flask-Limiter**: add a rate limit on `/login` (e.g. 5 min) per IP.
     - Dependency: `Flask-Limiter` (needs adding to `requirements.txt`)
     - Preferred for clear rate-limiting semantics
  - **Session/IP in-memory counter** (back-up): track failed attempts with timestamps and enorce cooldown.
     - Note: in-memory limiting is not distributed safe in prod, but OK for demo

### Testing Plan
Assuming pyrest or unittest is not currently set up in the repo, the following tests should be added in a follow-up change:

- Unit: hash generation/check works (password check true/false)
- Integration: POST `/login` with invalid creds returns flash message, does not set session
- Integration: throttle triggers after N failures (verify status code or message)

### Rollout / Rollback
- Rollout: add new config knobs with safe defaults; deploy to dev first
- Rollback: revert to previous auth behavior by removing rate limiter or disabling throttling flag (if implemented)
