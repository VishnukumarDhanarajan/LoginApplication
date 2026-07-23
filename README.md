# LoginApplication

Simple Flask login demo.

## Setup

1. Install dependencies:

   ``log
   pip install -r requirements.txt
   ```

2. Export the required secret key env variable:

   ```log
   export SECRET_KEY="your-strong-random-secret"
   ```

   The app will fail fast on startup if `SECRET_KEY` finds no value.

3. Run the app:

   ``log
   python app.py
   ```

## Demo credentials

The demo user store is in-memory and stores only hashed passwords.

- Username: `admin`
- Password: `password123`

> NOTE: In a real production app, replace the demo user store with a proper database and don't check secrets into version control.
