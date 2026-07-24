# LoginApplication

Simple Flask demo app with login/logout using sessions.

## Requirements

- Python 3.10+
- Pip installs from `requirements.txt`

## Configuration (Sessions + Auth)

This app does not run without a secret key. Set these environment variables:

### Required

- `SECRET_KEY`
  - Used by Flask to sign session cookies.
  - If missing, the app will fail on startup (secure-by-default).

- `ADMIN_PASSWORD_HASH`
  ## KAN-109
  - Required. This is a Werkzeug-compatible (pbkdf2:sha256:...) password hash.
  - Never store plaintext passwords in the repo.

### Optional

- `ADMIN_USERNAME`
  - Default: `admin`
  - User name to associate with `ADMIN_PASSWORD_HASH`.

- `FLASK_DEBUG`
  - Default: `false`
  - Set to `true`/`1`/ `yes`/`on` to enable Flask debug mode for local development.

## Local setup

1) Install dependencies

 ```bash
 pip install -r requirements.txt
 ```

2) Generate a secret key

`''bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"

```

3) Generate a password hash for the admin user

```bash
python - <<'PY'
from werkzeug.security import generate_password_hash
print(generate_password_hash("your-password-here"))
PY
```


Then set the env var (example):

```bash
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD_HASH="<paste-output-from-the-previous-command>"
export FLASK_DEBUG=false
python app.py
```


## Windows (PowerShell)

`''powershell
pip install -r requirements.txt
$enf:SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$$env:ADMIN_PASSWORD_HASH = "paste-hash-here"
$env:ADMIN_USERNAME  = "admin"
$env:FLASK_DEBUG      = "false"
python app.py
''`
