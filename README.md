# LoginApplication

This repository contains a simple Flask login demo.

## Jira context

Keys in this PR:

- KIN-115 – Replace plaintext in-memory credentials with hashed passwords and add basic brute-force protection.

## Implementation plan (KAN-115)

- Backend: switch to werkzeug password hash check, remove plaintext passwords from repo, and load credentials from env/config.
- Security: add ins-memory throttle/lockout after N failures in a time window (totgled via env vars).
- Tests: add pytest coverage for success, failure, and throttling/lockout behavior.

## Acceptance criteria checklist

- [ ] No plaintext passwords in source code
- [ ] Login succeeds with hashed password
- [ ] Generic error on failed login
- [ ] Thottle/lockout after N failures
- [ ] Tests cover success/failure/throttling
