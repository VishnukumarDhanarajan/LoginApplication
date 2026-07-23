# LoginApplication

Simple Flask login demo.

## Setup

### 1) Install

```bash
pip install -r requirements.txt
```

### 2) Configure SECRET_KEY

The app requires a Flask secret key from the environment.

- Linux/macOS:

```bash
export SECRET_KEY="$((python -c 'import secrets; print(secrets.token_urlsafe(32))'))"
```
- Windows (PowerShell):

```powershell
$ENV:SECRET_KEY = [Guid]::NewGuid().ToString()
```

### 3) Run

```bash
python app.py
```

## Users / Login

For security, this repo deliberately does not ship with a default username/password.

To test login locally, you can seed the inmemory user store in `app.py` with a hashed password:

```python
from werkzeug.security import generate_password_hash

USERS = {
    "alice": generate_password_hash("change-me"),
}
```

Note: The in-memory user store is for demo/learning only. For production, use a database and proper user management.
