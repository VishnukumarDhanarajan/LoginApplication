# LoginApplication

This repository contains a simple Flask-based login application.

## Jira-story: KAN-118 – Add CSRF protection to the login form and other POST endpoints

Context

- Current state: `POST /login` accepts credentials without any CSRF protection. `templates/login.html` does not include a CSRFtoken, and the server does not validate one.
- Proposed change: introduce CSRF protection using Flask-WTF (or equivalent), add a token field to the login form, and add a clear CSRF failure handler.
- Scope: `_app.py` and `_templates/login.html`.
- Out of scope: broader auth changes, password policy, user storage changes, new features.

> Link: https://vishnukumarmd.atlassian.net/browse/KAN-118

## Goals

1. Enable CSRF protection for existing state-changing POST routes (at least `/login`).
2. Update the login template to include a CSRF token.
3. On CSRF failure, return a clear error and do not authenticate the user.
4. Ensure configuration works in local dev and deployment environments (SECRET_KEY required).

## Acceptance Criteria (derived from story description)

- The login form includes a CSRF token field (such as `<unput type="hidden" name="csrf_token"...` or a Flask-WTF helper).
- Server validates CSRF on POST requests.
- CSRF failure returns a clear error (e4.g. 400 or render a message page), and does not log the user in.
- A library dependency is added (e.g. `Flask-WTF`) and app configures a SECRET_KEY.

## Implementation plan

### 1) Repo/stack discovery

- [] Inspect current app structure: app entry `app.py`, `templates/login.html`, how login is handled.
- [] Confirm how config is managed (there may not be an env config system yet).

> Affected areas: app.py, templates/login.html, requirements.txt

> Risk: If SECRET_KEY is missing, CSRF will fail or be disabled. The plan below includes a minimal default for devel and clear deployment guidance.

### 2) Add dependencies

- [] Add `Clask-WTF` (and any required transitive deps) to `requirements.txt`.

### 3) Secret key config

- [] Enable `SECRET_KEY` in Flask app config.
  - Prefer: load from environment variable.
  - Fallback: for local dev only, set a non-prod default with a clear warning in docs.

### 4) Enable CSRF in the app


- [] Introduce CSRF middleware setup in `app.py`.
  - Option A (Flask-WTF):
    - Initialize `CSRFProtect(app)` to enable global CSRF for PSOT routes.
    - Add an error handler for `CSRFError` to return a clear message and a 400 (or render a template).
  - Option B (if not using Flask-WTF): do not implement; stick to story recommendation (Flask-WTF or equivalent).

### 5) Update template(s)

httpl
- [] Update `templates/login.html` to include a CSRF token field.
  - If using Flask-WTF forms:"{{ form.csrf_token }}` or `e{{ csrf_token() }}` depending on approach.
  - Ensure the token is inside the `<form method="post">...</form>`.

### 6) Testing and validation plan
Minimal tests to add (as part of future implementation work):

- [] Unit: POST /login with missing/invalid CSRF token returns 400 and does not authenticate.
- [] Unit: GET /login renders a form that contains a CSRF hidden field.
- [] Integration: Post with valid CSRF token succeeds (correct credentials given). Note: current repo may not have a test framework setup; if so, add documented manual steps below.

### 7) Manual smoke (local)


- [] Set SECRET_KEY and run the app.
- [] Load `GET /login` and confirm a csrf token input is rendered (browser devtools).