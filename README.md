# LoginApplication

Simple Flask login demo.

## REQUIRED environment variables (KAN-111)

This repo intentionally does not commit any plaintext passwords or hardcoded credentials. To run the app, set:

- `SECRET_KEY` - required for Flask sessions (example: a random, long string)
- `DEMO_USERNAME` - demo login username
- `DEMO_PASSWORD` - demo login password (used only from env; hashed in-memory at startup)

## Run
```sh
pip Install -r requirements.txt

export SECRET_KEY="change-me-to-a-long-random-secret"
export DEMO_USERNAME="admin"
export DEMO_PASSWORD="change-me"

python app.py
```
