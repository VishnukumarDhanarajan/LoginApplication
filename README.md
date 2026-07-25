# Flask Login Application

## Setup

### Environment variable

This application requires a `SECRET_KEY` environment variable. Without it the
server will refuse to start.

**Windows PowerShell:**
```
$env:SECRET_KEY = "replace-with-a-long-random-string"
```

**macOS / Linux / Git Bash:**
```
export SECRET_KEY="replace-with-a-long-random-string"
```

Then start the development server:
```
flask run
```

## Demo credential

Use the following credential when testing locally:

| Field    | Value               |
|----------|---------------------|
| Email    | admin@example.com   |
| Password | password123         |

> This is a hardcoded demo credential stored in plain text. It is not suitable
> for production use.
