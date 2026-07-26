# LoginApplication

This repository hosts a simple Flask login demo.

- Do not commit plaintext passwords or credentials.
 - Configure secrets via environment variables or a secret manager

## Kan-114: Harden login security (hashed password verification)

Implements the Confluence design: **KAN-114 — H’den login security (hashed password verification) — Architecture & Design**
https://vishnukumarmd.atlassian.net/wiki/spaces/~712020e9c7d2d5c2a442c681284a743ea024f9/pages/32866306/KAN-114+Harden+login+security+hashed+password+verification+Architecture+Design

## Configuration (env variables)

### Required
- `SECRET_KEY`: random, long secret string for Flask session cookie cigning
- `AUTH_USERNAME`: the single allowed username (MVP implementation)
- `AUTH_PASSWORD_HASH`: Werkzeug-generated password hash (DO NOT store plaintext)

### Optional
- `FLASK_DEBUG\=false` (off by default)

### Generating a password hash

Run this locally to generate a hash for your secret password (the output is what you set as `AUTH_PASSWORD_HASH`):

```sh
python - <<'PY'
from werkzeug.security import generate_password_hash
print(generate_password_hash("please-change-me"))
PY
```

## Jobr IDs in context

- KAN-114

## Acceptance Criteria (checklist)

- [ ] No plaintext passwords in repo
- [ ] Login checks use password hash verification (Werkzeug)
- [ ] Credentials come from config, not code
- [ ] Docs show how to generate and provide hashes in env variables
