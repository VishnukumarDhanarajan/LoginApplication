# Change Log

**Project:** Flask Login Application — UI Enhancement: Field-Level Visual Validation and Focus States
**Date:** 2026-07-25
**Implementer:** Approved Change Implementer Agent
**Source documents:** impl-plan.md, architecture.md, design-review.md

---

## Approved Recommendations Implemented

All five approved tasks from impl-plan.md have been implemented in dependency order.

---

## TASK-001 — Update demo credential in app.py

**Status:** Complete

**File changed:** `app.py`

**What changed:** Line 25 — USERS dict key changed from `"admin"` to `"admin@example.com"`. No other line was modified.

**Before:**
```python
    "admin": "password123",
```
**After:**
```python
    "admin@example.com": "password123",
```

**Design decisions applied:** DD-07 (sole backend change is the USERS dict key; route logic, session management, and all other Python code untouched)

**Requirements satisfied:** FR-004, DIR-002, DIR-003, AC-5

---

## TASK-002 — Update HTML input structure in login.html

**Status:** Complete

**File changed:** `templates/login.html`

**Change A — novalidate on form element (line 62 of original):**

Added `novalidate` attribute to the `<form>` tag. Suppresses the browser-native tooltip balloon on submit, eliminates AT double-announcement, and gives JavaScript full ownership of validation feedback UI.

**Change B — Username input replaced with wrapper structure (line 63 of original):**

Replaced bare `<input type="text" name="username" ...>` with:
- `<div class="input-wrapper">` — creates `position: relative` containing block for the icon span
- `<input type="email" id="email" name="username" placeholder="Email" required aria-describedby="email-error" aria-invalid="false">` — email type enables Constraint Validation API; name="username" preserves the POST contract (DIR-001)
- `<span id="email-icon" class="field-icon" aria-hidden="true"></span>` — icon span with id (DD-03) and aria-hidden (NFR-006)
- `<span id="email-error" class="error-hint" role="status"></span>` — error hint span; role="status" provides implicit aria-live="polite"; explicit aria-live omitted (L-003, FU-05)

Password field: not modified (no wrapper, no ARIA attributes, no changes).

**Design decisions applied:** DD-01 (novalidate), DD-03 (id="email-icon" for getElementById), DD-05 (dual visual signal), L-003/FU-05 (no aria-live on error span)

**Requirements satisfied:** FR-001, FR-002, FR-003, NFR-004, NFR-006, DIR-001, AC-2, AC-3, AC-4, AC-5

---

## TASK-003 — Add CSS validation and focus styles in login.html

**Status:** Complete

**File changed:** `templates/login.html`

**What changed:** Eight new CSS rule groups appended inside the existing `<style>` block, immediately after the closing brace of `.error { }`. Rules declared in this exact order (order is load-bearing for CSS specificity):

1. `.input-wrapper` — `position: relative; display: block; margin: 0.4rem 0`
2. `.input-wrapper input` — `margin: 0; width: 100%; box-sizing: border-box`
3. `.field-icon` — absolute positioning at right edge of input; `display: none` by default
4. `input:focus` — `border-color: #1877f2; outline: none; box-shadow: 0 0 0 3px rgba(24,119,242,0.2)` — declared BEFORE .invalid and .valid so validation border colors win by source-order precedence when both are active (DD-05, FR-007)
5. `input.invalid` — `border-color: #d32f2f; padding-right: 2rem`
6. `input.valid` — `border-color: #2e7d32; padding-right: 2rem`
7. `.error-hint` — `display: block; font-size: 0.75rem; color: #d32f2f; min-height: 1em; margin-top: 0.15rem`
8. `@media (prefers-reduced-motion: no-preference) { input { transition: border-color 0.12s ease; } }` — transition gated behind reduced-motion query (L-001, FU-03)

No `box-shadow: none` added to `.invalid` or `.valid` — the blue focus ring co-exists with validation border colors intentionally (DD-05, NFR-005).

**Design decisions applied:** DD-05 (source-order cascade, dual visual signal), DD-06 (#1877f2 focus color), L-001/FU-03 (prefers-reduced-motion guard)

**Requirements satisfied:** FR-005, FR-006, FR-007, FR-008, FR-010, FR-011, FR-016, NFR-001, NFR-005, NFR-007, AC-1, AC-2, AC-3

---

## TASK-004 — Add JavaScript validation state machine in login.html

**Status:** Complete

**File changed:** `templates/login.html`

**What changed:** `<script>` block inserted immediately before `</body>` (not in `<head>`; no DOMContentLoaded wrapper needed when placed at end of body).

Key implementation details:
- Uses `var` for broadest browser compatibility (not `const`/`let`)
- Three DOM references via `getElementById` (DD-03): `#email`, `#email-icon`, `#email-error`
- `validateEmail()` implements a three-state machine: neutral (empty) / invalid (non-empty, validity.valid=false) / valid (non-empty, validity.valid=true)
- Neutral branch: removes both `.invalid` and `.valid`, sets `aria-invalid="false"`, hides and empties icon, clears hint
- Invalid branch: removes `.valid`, adds `.invalid`, sets `aria-invalid="true"`, sets icon textContent to `'⚠︎'` (U+26A0 + U+FE0E text variation selector — forces monochrome rendering so CSS color applies on iOS/macOS/Windows, DD-02, M-001 fix), sets icon color to `#d32f2f`, shows icon, sets hint text
- Valid branch: removes `.invalid`, adds `.valid`, sets `aria-invalid="false"`, sets icon to `'✓'` (U+2713, no emoji variant, no variation selector needed), sets icon color to `#2e7d32`, shows icon, clears hint text
- Null guard `if (emailInput) { ... }` wraps event listener registration (DD-04)
- `input` event fires on every keystroke; `blur` event fires on tab-out (handles paste-then-tab, A-03)
- All DOM writes use `textContent` only — never `innerHTML` (security control, no XSS vector)

**Design decisions applied:** DD-02 (U+FE0E variation selector), DD-03 (getElementById), DD-04 (null guard)

**Requirements satisfied:** FR-009, FR-013, FR-014, FR-015, FR-017, FR-018, FR-019, FR-020, NFR-001, NFR-002, NFR-003, NFR-004, NFR-006, AC-2, AC-3, AC-4

---

## TASK-005 — Create README.md

**Status:** Complete

**File created:** `README.md` (new file — did not exist before)

**What was added:**
- Title and Setup section
- SECRET_KEY environment variable instructions for Windows PowerShell (`$env:SECRET_KEY = "..."`) and macOS/Linux/Git Bash (`export SECRET_KEY="..."`)
- `flask run` command to start the server
- Demo credential table: email `admin@example.com`, password `password123`
- Disclaimer that credentials are hardcoded demo values not suitable for production

**Design decisions applied:** DD-07 (credential value confirmed from TASK-001)

**Requirements satisfied:** DIR-003, L-004, FU-04, AC-5

---

## Validation Runs

### Automated structural checks — all PASS

| Check | Result |
|---|---|
| app.py line 25: `"admin@example.com": "password123"` | PASS |
| app.py: old key `"admin"` absent | PASS |
| login.html: `novalidate` on form | PASS |
| login.html: `class="input-wrapper"` present | PASS |
| login.html: `type="email"` on email input | PASS |
| login.html: `id="email"` on email input | PASS |
| login.html: `name="username"` on email input | PASS |
| login.html: `aria-describedby="email-error"` on email input | PASS |
| login.html: `aria-invalid="false"` initial value | PASS |
| login.html: `id="email-icon"` on icon span | PASS |
| login.html: `aria-hidden="true"` on icon span | PASS |
| login.html: `role="status"` on error hint span | PASS |
| login.html: no `aria-live` attribute present | PASS |
| login.html: password input structurally unchanged | PASS |
| login.html: `input:focus` declared before `input.invalid` | PASS |
| login.html: `.input-wrapper` rule present | PASS |
| login.html: `.field-icon` rule present | PASS |
| login.html: `input.invalid` rule present | PASS |
| login.html: `input.valid` rule present | PASS |
| login.html: `.error-hint` rule present | PASS |
| login.html: `prefers-reduced-motion` media query present | PASS |
| login.html: no `box-shadow: none` in .invalid/.valid | PASS |
| login.html: `<script>` placed before `</body>` | PASS |
| login.html: `<script>` not in `<head>` | PASS |
| login.html: uses `var` (not const/let) | PASS |
| login.html: null guard `if (emailInput)` present | PASS |
| login.html: `addEventListener('input', validateEmail)` | PASS |
| login.html: `addEventListener('blur',  validateEmail)` | PASS |
| login.html: no `innerHTML` usage | PASS |
| login.html: warning icon U+26A0 present | PASS |
| login.html: warning icon U+FE0E variation selector present | PASS |
| README.md: exists | PASS |
| README.md: contains `admin@example.com` | PASS |
| README.md: contains `password123` | PASS |
| README.md: contains `SECRET_KEY` instructions | PASS |
| README.md: contains Windows PowerShell instructions | PASS |
| README.md: contains macOS/Linux export instructions | PASS |

### NFR-011 Line Count

New CSS lines added to login.html: 36
New JS lines added to login.html: 37 (35 non-blank)
Combined total (including blank lines): 73
NFR-011 budget: 80
Status: PASS (73 <= 80)

---

## Design Decisions Traceability

| Decision ID | Description | Applied in |
|---|---|---|
| DD-01 | Add `novalidate` to `<form>` element | TASK-002A |
| DD-02 | Use U+26A0 + U+FE0E text variation selector for warning icon | TASK-004 |
| DD-03 | Use `id="email-icon"` + `getElementById` (not sibling selector) | TASK-002B, TASK-004 |
| DD-04 | Null guard wraps event listener registration | TASK-004 |
| DD-05 | Dual visual signal (blue box-shadow + validation border) is intentional; `input:focus` declared before `.invalid`/`.valid` | TASK-003, TASK-004 |
| DD-06 | `#1877f2` accepted for focus border color | TASK-003 |
| DD-07 | USERS dict key update is the sole backend change | TASK-001 |

---

## Scope Creep Verification

No unapproved changes were made. The following items were explicitly excluded and remain unchanged:

- Flask routes (`/login`, `/dashboard`, `/logout`) — not modified
- Session logic — not modified
- Flash message handling — not modified
- Password input HTML — structurally unchanged (no wrapper, no ARIA attributes)
- `request.form.get("username")` — not modified (POST field name contract preserved)
- Pre-existing XSS in dashboard route (FU-02) — out of scope, not touched
- Missing `<label>` elements (FU-01) — out of scope, not added
- Any external file outside `app.py`, `templates/login.html`, `README.md` — not touched

---

## Remaining Approved Items

All five approved tasks (TASK-001 through TASK-005) are complete. TASK-006 (end-to-end verification) requires a live browser and a running Flask server with SECRET_KEY set; it is a manual QA step outside the scope of automated implementation.

---

## Blockers and Risks

No implementation blockers encountered.

Residual risks from architecture.md (unchanged by implementation):
- R-01: `validity.valid` edge-case variation across browsers — accepted for this story scope
- R-02: Icon misalignment on viewports narrower than 300px — mitigation is to test at 320px; media query can be added if overlap is observed
- R-NEW-01: U+26A0 emoji rendering — mitigated by U+FE0E variation selector (confirmed in TASK-004)

---

*Handoff to peer-code-reviewer agent.*
