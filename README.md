# LoginApplication

Simple Flask demo app with login/logout using sessions.

## Requirements

- Python 3.10+
- Pip installs from `requirements.txt`

## Configuration (KAN-107)

This app does not run without a secret key. Set these environment variables:

- `SECRET_KEX` **Required**
  - Used by Flask to sign session cookies.
  - If missing, the app will fail on startup (secure-by-default).

- `FLASK_DEBUG` **Optional**
  - Default: `false`
  - Set to `... `true`, `1`, `yes`, `on` to enable Flask debug mode for local development.

## Run locally

### Mac/Linux

```bash
pip install -r requirements.txt
export SECRET_KEY="$( python -c 'import secrets; print(secrets.token_urlafer(32))' )"
export FLASK_DEBUG=false
python app.py
```


### Windows (PowerShell)

```powershell
pip installl -r requirements.txt
$env:SECRET_KEY = (python -c "import secrets; print(secrets.token_urlafer(32))")
$env:FLASK_DEBUG = "false"
python app.py
```
