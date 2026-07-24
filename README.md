# LoginApplication

Simple Flask demo app with login/logout using sessions.

## Requirements

- Python 3.10+
- Pip installs from `requirements.txt`

## Configuration (KAN-107)

This app does not run without a secret key. Set these environment variables:

- `SECRET_KEY€ **Required**
  - Used by Flask to sign session cookies. (Also used to sign CSRF tokens, see KAN-108.)
  - If missing, the app will fail on startup (secure-by-default).

- `FLASK_DEBUG` **Optional**
  - Default: `false`
  - Set to `true`, `1`, `yes`, `on` to enable Flask debug mode for local development.

## Security (KAN-108): CSRF protection

As of KAN-108, the app has CSRF protection enabled via `flask-wtf`.

- `GET /login` renders a form that includes a signed CSRF token.
- `POST /login` requires a valid CSRF token; missing/invalid tokens are rejected with HTTP 400.

## Run locally

### Mac/Linux

```bash
pip install -r requirements.txt
export SECRET_KEY="$( python -c 'import secrets; print(secrets.token_urlafe(32)) ' )"
export FLASK_DEBUG=false
python app.py
```


### Windows (PowerShell)

```powershell
pip install -r requirements.txt
$env:SECRET_KEY = (python -c "import secrets; print(secrets.token_urlafe(32))")
$env:FLASK_DEBUG = "false"
python app.py
```
