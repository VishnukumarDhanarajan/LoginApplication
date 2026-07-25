# PR Review Checklist

**PR Title:** feat: field-level visual validation and focus states for login form
**Date:** 2026-07-25
**Reviewer:** ___________________________

---

## Instructions

Work through each section in order. Mark each item as:
- `[x]` — Confirmed passing
- `[-]` — Not applicable
- `[!]` — Issue found (add a comment below the item)

All items in sections 1–7 must be checked before approving. Section 8 (known post-merge items) requires the reviewer to confirm they have been read and accepted.

---

## 1. HTML Correctness

- [ ] The `<form>` element has the `novalidate` attribute (login.html line 98)
- [ ] The email input has `type="email"` (not `type="text"`) (line 100)
- [ ] The email input has `name="username"` — the POST field name contract is preserved (line 100)
- [ ] The email input has `id="email"` (required by JS getElementById) (line 100)
- [ ] The email input has `placeholder="Email"` (line 100)
- [ ] The email input has `required` attribute (line 100)
- [ ] The email input has `aria-describedby="email-error"` (line 100)
- [ ] The email input has `aria-invalid="false"` as the initial static value (line 100)
- [ ] The icon span has `id="email-icon"` (line 101)
- [ ] The icon span has `class="field-icon"` (line 101)
- [ ] The icon span has `aria-hidden="true"` — decorative glyph, not read by screen readers (line 101)
- [ ] The error hint span has `id="email-error"` (line 103)
- [ ] The error hint span has `class="error-hint"` (line 103)
- [ ] The error hint span has `role="status"` (line 103)
- [ ] The error hint span does NOT have an explicit `aria-live` attribute — `role="status"` already implies `aria-live="polite"` (line 103)
- [ ] The password input is structurally unchanged: `type="password"`, `name="password"`, `placeholder="Password"`, `required` — no wrapper div, no ARIA attributes added (line 104)
- [ ] Neither input has the `.invalid` or `.valid` class set statically in HTML — both classes must be absent on page load

---

## 2. CSS Correctness

- [ ] `.input-wrapper` rule is present with `position: relative` (required for icon absolute positioning)
- [ ] `.input-wrapper input` rule sets `margin: 0` (prevents double spacing with wrapper margin)
- [ ] `.field-icon` rule has `position: absolute`, `right: 0.6rem`, `top: 50%`, `transform: translateY(-50%)`, `pointer-events: none`, `display: none` by default
- [ ] `input:focus` rule is declared BEFORE `input.invalid` and `input.valid` in the stylesheet (source order is load-bearing — validation border colors must win over focus blue when both are active)
- [ ] `input:focus` sets `border-color: #1877f2`
- [ ] `input:focus` sets `outline: none` AND `box-shadow: 0 0 0 3px rgba(24, 119, 242, 0.2)` — the box-shadow replaces the native outline as the accessible focus ring
- [ ] `input.invalid` sets `border-color: #d32f2f` and `padding-right: 2rem`
- [ ] `input.valid` sets `border-color: #2e7d32` and `padding-right: 2rem`
- [ ] Neither `.invalid` nor `.valid` has `box-shadow: none` — the blue focus ring must co-exist with validation border colors (DD-05 dual signal is intentional and must be preserved)
- [ ] `.error-hint` has `display: block`, `font-size: 0.75rem`, `color: #d32f2f`, `min-height: 1em` (layout reserved even when empty)
- [ ] The CSS `transition: border-color 0.12s ease` is wrapped in `@media (prefers-reduced-motion: no-preference)` — not applied unconditionally

---

## 3. JavaScript Correctness

- [ ] The `<script>` block is placed immediately before `</body>` — not in `<head>`, no `DOMContentLoaded` wrapper needed
- [ ] DOM references use `document.getElementById` (not `querySelector` with adjacent sibling combinator) for all three: `#email`, `#email-icon`, `#email-error`
- [ ] `validateEmail()` function handles all three branches: empty (neutral), non-empty invalid, non-empty valid
- [ ] Neutral branch: removes both `.invalid` and `.valid` classes, sets `aria-invalid="false"`, hides icon, clears icon text, clears hint text
- [ ] Invalid branch: removes `.valid`, adds `.invalid`, sets `aria-invalid="true"`, sets icon `textContent` to the warning character with U+FE0E variation selector, sets icon color to `#d32f2f`, shows icon, sets hint text to "Please enter a valid email address."
- [ ] Valid branch: removes `.invalid`, adds `.valid`, sets `aria-invalid="false"`, sets icon `textContent` to `✓`, sets icon color to `#2e7d32`, shows icon, clears hint text
- [ ] Warning icon assignment uses U+26A0 + U+FE0E text variation selector (forces monochrome text rendering on iOS/macOS/Windows — prevents yellow/orange emoji rendering that would break NFR-003)
- [ ] `if (emailInput)` null guard wraps the `addEventListener` calls — prevents TypeError if template rendering removes the element
- [ ] Both `input` and `blur` events are registered on `emailInput`
- [ ] All DOM writes use `textContent` exclusively — NO `innerHTML` anywhere in the script block (XSS prevention)
- [ ] No `async`/`await`, `fetch`, `XMLHttpRequest`, `setTimeout`, `eval`, or `new Function` calls in the JS block (NFR-002 compliance)

---

## 4. Accessibility

- [ ] Focus indicator is visible in standard browsers: blue `box-shadow` ring appears when either field is focused (NFR-005)
- [ ] Validation state is conveyed by both color AND icon — icon supplements color so users who cannot distinguish red from green still receive information (NFR-003)
- [ ] `aria-invalid` is updated correctly by JS: `"true"` on invalid, `"false"` on valid or neutral (NFR-004, FR-013)
- [ ] `aria-describedby` on the email input references `#email-error`, which is populated with a description when invalid (NFR-004, FR-014)
- [ ] Icon span has `aria-hidden="true"` — the Unicode glyph is decorative; meaning is conveyed via `aria-invalid` and `aria-describedby` (NFR-006)
- [ ] `role="status"` on `#email-error` ensures screen readers announce validation hint text changes without interrupting currently-spoken content
- [ ] No external CSS or JS libraries are referenced — zero additional network requests (NFR-010)
- [ ] **Note (post-merge item M-001):** The `input:focus` rule suppresses `outline` without a `@media (forced-colors: active)` fallback. Keyboard-only users in Windows High Contrast Mode will not see a focus indicator. This is accepted for this release with documented deferral rationale. Confirm this is accepted.

---

## 5. Security

- [ ] All JavaScript DOM writes use `textContent` — no `innerHTML` usage (prevents XSS if any user-typed value were ever reflected)
- [ ] No user-typed input is written to the DOM by any JS path — icon content and hint text are hardcoded string literals only
- [ ] No `eval()`, `new Function()`, or dynamic code execution in the JS block
- [ ] `app.py` SECRET_KEY enforcement (lines 7–13) is unchanged
- [ ] pip-audit result reviewed: no known vulnerabilities in Flask 3.1.3 / Werkzeug 3.1.8 (confirmed in code-review.md)
- [ ] Pre-existing XSS in `app.py` line 59 (`session['user']` interpolated into HTML f-string) is noted. Not introduced by this PR; harmless with the current hardcoded USERS dict. Tracked as future story item FU-02.

---

## 6. Backend Change

- [ ] Only `app.py` line 25 was modified — the USERS dict key changed from `"admin"` to `"admin@example.com"`. No other Python code was changed.
- [ ] `request.form.get("username", "").strip()` on the login route (line 41) is unchanged — the POST field name contract is preserved
- [ ] All routes (`/`, `/login`, `/dashboard`, `/logout`) are structurally unchanged
- [ ] Session management, flash messages, and redirect logic are unchanged
- [ ] Flask server starts without error with a valid SECRET_KEY environment variable set

---

## 7. Documentation

- [ ] `README.md` exists at the project root
- [ ] `README.md` documents the updated demo credential: `admin@example.com` / `password123`
- [ ] `README.md` includes SECRET_KEY environment variable instructions for Windows PowerShell and macOS/Linux/Git Bash
- [ ] **Note (post-merge item L-003):** `README.md` is missing `pip install -r requirements.txt` before the `flask run` command. A new developer without Flask installed will encounter an error. Confirm this is accepted for this release.
- [ ] SDLC pipeline artifacts are present in the repository root: `requirements.md`, `architecture.md`, `design-review.md`, `impl-plan.md`, `change-log.md`, `verification-report.md`, `code-review.md`

---

## 8. Known Post-Merge Items — Confirm Acceptance

The following findings were identified in the code review and are intentionally not fixed in this PR. The reviewer must confirm they have read each item and accept deferral.

- [ ] **M-001 ACCEPTED** — Missing `forced-colors` media query; keyboard focus invisible in Windows High Contrast Mode. Fix: `@media (forced-colors: active) { input:focus { outline: 2px solid; } }` (3 lines, within NFR-011 budget). Deferral rationale: WCAG 2.1 Level AA does not explicitly mandate forced-colors support; fix is trivial and can be applied in a follow-up accessibility story.
- [ ] **L-001 ACCEPTED** — Incomplete null guard: `emailIcon` and `emailError` not checked inside `validateEmail()`. Fix: `if (emailInput && emailIcon && emailError)`. Risk is low: both elements are present in the current template.
- [ ] **L-002 ACCEPTED** — Neutral branch leaves stale `emailIcon.style.color` on hidden element. Fix: `emailIcon.style.color = '';` in neutral branch. Risk is low: element is hidden via `display: none`; stale style has no visible effect.
- [ ] **L-003 ACCEPTED** — README missing `pip install -r requirements.txt` step. Fix: add install step to Setup section. Risk: new developers without Flask pre-installed cannot start the server by following only the README.
- [ ] **L-004 ACCEPTED** — Missing `autocomplete="email"` and `autocomplete="current-password"`. Fix: add respective `autocomplete` attributes to both inputs. Risk: inconsistent browser/password-manager autofill behavior; WCAG 2.1 SC 1.3.5 gap.

---

## Final Sign-Off

| Review Area | Status |
|---|---|
| HTML Correctness (Section 1) | |
| CSS Correctness (Section 2) | |
| JavaScript Correctness (Section 3) | |
| Accessibility (Section 4) | |
| Security (Section 5) | |
| Backend Change (Section 6) | |
| Documentation (Section 7) | |
| Known Post-Merge Items (Section 8) | |

**Reviewer Decision:**

- [ ] Approve
- [ ] Request changes (specify in PR comments)

**Reviewer Signature / GitHub Handle:** ___________________________
**Date Reviewed:** ___________________________
