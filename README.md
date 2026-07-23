# LoginApplication

Simple Flask login demo.

## Running the app

19 Install dependencies:

```
pip install -r requirements.txt
```

2 Set a secret key (KAN-104)

Flask requires a SECRET_KEY to sign session cookies. This project does not hardcode it; you must provide it via an environment variable:

```
export SECRET_KEY='replace-with-a-strong-random-value'
```

Memo: don't use a weak or committed value.

3 Run:

```
python app.py
```

## Demo credentials

- Username: `admin`
- Password: `password123`

Note: the password is stored as a hash in code (for demo purposes) and verified using Werkzeug +Flask.