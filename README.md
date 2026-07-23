# LoginApplication

Simple Flask login demo (educational).

## Quick start

1. Create a virtualenv (optional)
    ```bash
    python -m venv .venv
    source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
    ```

2. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```

3. Set required env vars

   **REQUIRED**

    - `SECRET_KEY`: Flask session signing secret (don't hardcode in code).

    *Optional*

    - `FLASK_DEBUG`: set to `true` (or `1`) to enable debug. Default: false.

    Example:
    ```bash
    export SECRET_KEY="change-me-random-string"
    export FLASK_DEBUG=true
    ```

4. Run the app
    ```bash
    python app.py
    ```

5. Open http://127.0.0.1:5000/

## Security notes

- THIS IS A DEMO. Do not use the in-memory user store in production.
- Passwords are stored as hashes (not plaintext).
- Login POST is protected by CSRF (Flask-WTF) and will reject missing/invalid tokens.
