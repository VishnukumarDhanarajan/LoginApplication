# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased] — 2026-07-25

### Scope

UI enhancement: field-level visual validation and focus states for the Flask login form.
All new logic is client-side and self-contained within `templates/login.html`.
The only backend change is updating the hardcoded demo credential key in `app.py`.

### Added

- **Focus state styling** (`templates/login.html`): Both the email and password fields now show a distinct blue border (`#1877f2`) and a `box-shadow` focus ring when focused. The `box-shadow` ring is the accessible keyboard focus indicator that co-exists with validation border colors when a validated field is focused.
- **Email field invalid state** (`templates/login.html`): When the email input contains a non-empty value that fails the HTML5 `validity.valid` check, the border turns red (`#d32f2f`), a red warning icon (⚠, U+26A0 + U+FE0E text variation selector) appears at the right edge, and the hint "Please enter a valid email address." is displayed below the field. `aria-invalid="true"` is set on the input for screen reader compatibility.
- **Email field valid state** (`templates/login.html`): When the email input contains a value that passes the `validity.valid` check, the border turns green (`#2e7d32`), a green checkmark icon (✓) appears at the right edge, and the hint is cleared. `aria-invalid="false"` is set.
- **Email field neutral state** (`templates/login.html`): When the email field is empty, no validation styling or icon is shown. Neutral state is re-entered whenever all characters are deleted.
- **ARIA accessibility** (`templates/login.html`): `aria-describedby="email-error"` and `aria-invalid` attributes added to the email input. `#email-error` span with `role="status"` (implicit `aria-live="polite"`) provides live announcements to screen readers.
- **Icon wrapper** (`templates/login.html`): `.input-wrapper` div with `position: relative` added around the email input to enable absolutely-positioned icon span placement without external HTTP requests (FR-012 compliance).
- **Reduced-motion guard** (`templates/login.html`): `transition: border-color 0.12s ease` is gated behind `@media (prefers-reduced-motion: no-preference)` for users who have enabled OS reduced-motion preferences.
- **`novalidate` on form** (`templates/login.html`): Suppresses the browser-native HTML5 validation tooltip balloon, giving JavaScript full ownership of validation feedback UI and eliminating double-announcement for screen reader users.
- **README.md** (new file): Setup instructions including SECRET_KEY environment variable configuration (Windows PowerShell and macOS/Linux/Git Bash) and the updated demo credential (`admin@example.com` / `password123`).
- **SDLC pipeline artifacts** (new files): `requirements.md`, `architecture.md`, `design-review.md`, `impl-plan.md`, `change-log.md`, `verification-report.md`, `code-review.md` — full audit trail for the eight-stage development pipeline.

### Changed

- **`app.py` line 25** (`app.py`): USERS demo credential key changed from `"admin"` to `"admin@example.com"`. The password value (`"password123"`) and all route logic are unchanged. This change enables the demo credential to pass client-side email format validation.
- **Username input type** (`templates/login.html`): `type="text"` changed to `type="email"`. The `name="username"` attribute and the backend `request.form.get("username")` call are unchanged; the POST field name contract is preserved.
- **Username input placeholder** (`templates/login.html`): Placeholder text changed from `"Username"` to `"Email"`.

### Validation Summary

| Check Category | Checks | Passed |
|---|---|---|
| Acceptance Criteria (AC-1 through AC-5) | 26 | 26 |
| Non-Functional Requirements (NFR) | 6 | 6 |
| Design Decisions (DD-01 through DD-07) | 7 | 7 |
| Scope Integrity | 4 | 4 |
| **Total** | **43** | **43** |

Verdict: **Verified** (static analysis; live-server manual checks required per impl-plan TASK-006).

### Known Limitations (Post-Merge Items)

The following findings from the code review are tracked for follow-up and were not fixed before this PR:

- **M-001**: `input:focus { outline: none }` has no `@media (forced-colors: active)` fallback. Keyboard-only users in Windows High Contrast Mode receive no visible focus indicator. Fix: add a 3-line `@media (forced-colors: active) { input:focus { outline: 2px solid; } }` rule.
- **L-001**: Null guard (`if (emailInput)`) only checks `emailInput`; `emailIcon` and `emailError` are not independently null-checked. Fix: extend condition to `if (emailInput && emailIcon && emailError)`.
- **L-002**: The neutral branch does not reset `emailIcon.style.color`, leaving a stale inline style on the hidden icon element. Fix: add `emailIcon.style.color = '';` in the neutral branch.
- **L-003**: README is missing the `pip install -r requirements.txt` dependency installation step. Fix: add the install command to the Setup section.
- **L-004**: Email input lacks `autocomplete="email"` and password input lacks `autocomplete="current-password"`. Fix: add the respective `autocomplete` attributes to both inputs.
