# LoginApplication

Simple Flask login demo.

## Running locally

1) Install dependencies:

```
pip install -r requirements.txt
```

2) Set required env variables:

- `SECRET_KEY`: required in non-debug runs (fail-fast if missing)
- `USERS_JSON`: JSON object mapping username -> password hash

Example:

 ```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32)))')"
export USERS_JSON='{"admin":"pbkdf2:sha256:260000$..."}'
```

To generate a hash for a password locally:

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))"
```

3) Run the app:

 ```bash
python app.py
```

## Debug mode
Debug is not enabled by default. For local development, use either:

- `flask run --debug`, or
- `export FLASK_DEBUG=1`
