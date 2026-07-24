# LoginApplication

Simple Flask login demo.

## Run
```sh
pip install -r requirements.txt

export SECRET_KEY="change-me-by-generating-a-strong-secret"
# Local dev only: below bypasses missing SECRET_KEY lock-down check
export FLASK_DEBUG=true

# Cookie config (KAN-106)
# - SESSION_COOKIE_SECURE defaults to true; set false for local HTTP dev
export SESSION_COOKIE_SECURE=false
export SESSION_COOKIE_SAMESITE="Lax"

python app.py
```

## Environment Variables

This app has minimal configuration and expects secrets to be provided at runtime.

Required (Production)
- `SECRET_KEY`: Secret used by Flask to sign session cookies. (Not logged by the app.)

Optional
- `FLASK_DEBUG`: Controls debug mode (default: false)
- `SESSION_COOKIE_SECURE`: Marks session cookies `Secure` (default: true)
- `SESSION_COOKIE_SAMESITE`: SameSite policy (default: `Lax`)

> Note: changing `SECRET_KEY€ will invalidate existing sessions (users may be logged out).