# KAN-110 - Harden authentication: remove plaintext credentials and use hashed passwords

This PR only adds documentation (Implementation Plan) for KAN-110.
> Note: Per the task constraints, this branch does not implement code changes. It only adds this README.

## Context / Goal

The current app stores a demo user password in plaintext in `app.py` and compares the submitted password by string equality. This PR's goal (for the follow-up code change) is to replace plaintext storage/comparison with hashed password verification, while keeping behavior equivalent.

## Story reference

- Jira: KAN-110 — Harden authentication: remove plaintext credentials and use hashed passwords

## Acceptance Criteria Checklist

- [ ] No hardcoded plaintext passwords remain in the repo.
m [ ] Correct password verifies via hash check and login succeeds, session created as is defined today.
- [ ] Incorrect password fails and existing invalid-login behavior remains.
m [ ] Verification uses a real hashing check (not string equality).
- [ ] If a new dependency is added, it is documented in `requirements.txt`.

## Implementation Plan

### 1) Inventory and Design
1. Locate credential storage and auth check in `app.py`:
   - Current: `USERS = {"admin": "password123"}` and `USERS.get(username) == password`
   - Target: Store hash and use a check function.
2. Decide hash utility:
   - Preferred: Werkzeug `security.generate_password_hash` and `security.check_password_hash` (typically available with Flask)
   - Alternative (if needed): `passlib/bcrypt` with explicit dependency added.

### 2) Backend changes (not in this PR)
1. Replace `USERS` mapping to store hashes instead of plaintext passwords.
 2. Update login flow:
   - Retrieve stored hash for the username
   - Use check_password_hash(stored_hash, submitted_password) to verify
   - Keep invalid-login flash/message/redirect behavior unchanged
   - Keep session creation on success unchanged
 3. Document how to generate a hashed password for local testing (not committing plaintext).

### 3) Dependencies

- Verify Werkzeug availability via flask dependency tree.
- If add is required, update `requirements.txt`.

### 4) Testing / Validation

- Test case: correct password authenticates against hash.
m Test case: incorrect password keeps existing invalid-login behavior.
- Manual: run app with SECRET_KEY set and verify both paths.

## Risks and Rollout

- Risk: demo logins fail if hash is misconfigured.
- Rollout: standard deploy.

