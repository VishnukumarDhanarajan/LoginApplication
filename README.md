# LoginApplication

This repository hosts a simple Flask login demo.

- Do not commit plaintext passwords or credentials.
- Configure secrets via environment variables or a secret manager

## Jira-To-PR Implementation Plan

## Jork IDs in context

- KAN-114

## Story
*HARDEN login security by removing hardcoded plaintext credentials and using hashed password verification.

## Scope/Goals

- Remove plaintext credentials from source control
- Replace direct password comparison with hash verification
- Move credentials out of `app.py` (minimally via env config)

## Acceptance Criteria (checklist)

- [ ] No plaintext passwords in repo
- [ ] Login checks use password hash verification (Werkzeug)
- [ ] Credentials come from config not code
- [ ] Docs show how to generate and provide hashes in env variables

## Tasks (ordered)

### 1) Backend (S, 1-2 hours)
- Replace in-code USERS map with env-driven user store
- Use `workzeug.security.check_password_hash` for verification
- Add clear startup errors when credentials are missing

### 2) Testing (S, 1-2 hours)
- Add unit or smoke tests for successful/failed login
- Grep/check that no plaintext passwords remain in the repo

### 3) Docs (S, ~30 mins)
- Document required env variables (SECRET_KEY, LOGIN_USER, LOGIN_PASSWORD_HASH (TBD))
- Provide safe examples without secrets

## Risks/Dependencies
- Runtime env must provide credential config
- Details of persistent user store are TFD

## Rollout/Rollback
- Rollout: deploy with env vars set in staging
- Rollback: revert this PR to restore previous behavior (not recommended in prod)
