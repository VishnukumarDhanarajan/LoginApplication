# Implementation Plan
**Project:** Flask Login Application — UI Enhancement: Field-Level Visual Validation and Focus States
**Planner:** Implementation Planner Agent
**Date:** 2026-07-25
**Source documents:** requirements.md (2026-07-25), architecture.md (2026-07-25), design-review.md (2026-07-25)
**Gate status:** Design review APPROVED WITH MINOR COMMENTS — pipeline cleared for implementation

---

## 1. Scope and Sequencing Basis

### What is being built

A client-side visual enhancement to the existing Flask login form. The work touches exactly two files:

- `app.py` — one line change: USERS dict key from `"admin"` to `"admin@example.com"` (FR-004, DIR-002)
- `templates/login.html` — HTML restructure of the email input, new CSS rules for focus/validation states, a new inline JavaScript validation state machine
- `README.md` — new file documenting the updated demo credential and SECRET_KEY setup (DIR-003)

No changes are made to routes, session logic, flash messages, the dashboard, the password field behavior, or any external files.

### Sequencing logic

1. The backend credential change (TASK-001) and the HTML structure change (TASK-002) have no mutual dependency and can be executed in parallel by different contributors, or sequentially by one developer.
2. CSS (TASK-003) must follow TASK-002 because the CSS class selectors (`.input-wrapper`, `.field-icon`, `input.invalid`, `input.valid`, `.error-hint`) and element IDs reference elements that TASK-002 introduces.
3. JavaScript (TASK-004) must follow both TASK-002 (it references `id="email"`, `id="email-icon"`, `id="email-error"`) and TASK-003 (it toggles class names defined in the CSS).
4. README (TASK-005) depends on TASK-001 being final so the credential value it documents is confirmed.
5. End-to-end verification (TASK-006) requires all five prior tasks to be complete.

### Line budget constraint

NFR-011 limits new CSS and JavaScript lines added to `login.html` to 80 combined. The architecture estimates approximately 71 lines for the combined CSS and JavaScript additions. The developer must count actual added lines before committing; inline comments should be kept minimal to stay within budget.

---

## 2. Workstreams

| Workstream | Tasks | Description |
|---|---|---|
| Backend | TASK-001 | Credential update in app.py |
| Frontend | TASK-002, TASK-003, TASK-004 | All login.html changes (HTML structure, CSS, JavaScript) |
| Documentation | TASK-005 | README.md creation |
| QA / Verification | TASK-006 | Manual end-to-end acceptance check |

---

## 3. Prioritized Dependency-Ordered Task Backlog

---

### TASK-001 — Update demo credential in app.py

| Field | Value |
|---|---|
| Task ID | TASK-001 |
| Workstream | Backend |
| Owner role | Backend Engineer |
| Complexity | XS |
| Dependencies | None |
| Requirement coverage | FR-004, DIR-002, DIR-003, AC-5 |

**File to change:** `app.py`

**Exact change description:**

Locate line 25 in `app.py`:
```python
    "admin": "password123",
```
Replace the key only. Do not change the password value, the surrounding dict syntax, or any other line:
```python
    "admin@example.com": "password123",
```
No other change is made to `app.py`. The route handler at line 41 reads `request.form.get("username")` and does a dict lookup — this lookup will now match when the submitted value is `admin@example.com`. No route logic change is needed.

**Definition of done / Acceptance test:**

1. Open `app.py` and verify line 25 reads exactly `"admin@example.com": "password123",`.
2. Verify no other line in `app.py` was modified (diff should show exactly one character-range change: `"admin"` → `"admin@example.com"`).
3. Run `flask run` with a valid `SECRET_KEY` environment variable set and confirm the server starts without error.
4. Submit the form with `admin@example.com` and `password123` and confirm redirect to `/dashboard` (full AC-5 test requires TASK-002 through TASK-004 to also be complete, but the credential lookup can be tested via curl: `curl -X POST http://127.0.0.1:5000/login -d "username=admin@example.com&password=password123" -L` should return dashboard content).

---

### TASK-002 — Update HTML input structure in login.html

| Field | Value |
|---|---|
| Task ID | TASK-002 |
| Workstream | Frontend |
| Owner role | Frontend Engineer |
| Complexity | S |
| Dependencies | None |
| Requirement coverage | FR-001, FR-002, FR-003, DD-01, DD-03, DD-05, L-003, NFR-004, NFR-006, DIR-001, AC-2, AC-3, AC-4, AC-5 |

**File to change:** `templates/login.html`

**Exact change description:**

Two changes are required in `login.html`.

**Change A — Add `novalidate` to the form element (line 62).**

Current line 62:
```html
        <form method="POST" action="{{ url_for('login') }}">
```
Replace with:
```html
        <form method="POST" action="{{ url_for('login') }}" novalidate>
```
Rationale (DD-01): `novalidate` suppresses the browser-native tooltip balloon on submit, eliminates double-announcement for screen reader users who would otherwise hear both the native popup and the `aria-invalid` announcement, and gives JavaScript full ownership of all validation feedback UI. With `novalidate`, blank-field submission is handled by the server (which rejects unrecognized credentials and flashes an error message) rather than by the browser. This supersedes the native-validation fallback clause in NFR-012 as agreed in the design review.

**Change B — Replace the bare username input (line 63) with the wrapper structure.**

Current line 63:
```html
            <input type="text" name="username" placeholder="Username" required>
```
Replace with the following block (7 lines):
```html
            <div class="input-wrapper">
                <input type="email" id="email" name="username" placeholder="Email" required aria-describedby="email-error" aria-invalid="false">
                <span id="email-icon" class="field-icon" aria-hidden="true"></span>
            </div>
            <span id="email-error" class="error-hint" role="status"></span>
```

Attribute-by-attribute rationale:
- `type="email"` — FR-001: enables the HTML5 Constraint Validation API (`validity.valid`) used by the JS state machine.
- `id="email"` — Required by `document.getElementById('email')` in TASK-004 (DD-03).
- `name="username"` — FR-002, DIR-001: the POST payload key is unchanged; the Flask route reads `request.form.get("username")` without modification.
- `placeholder="Email"` — FR-003.
- `required` — A-09: retained for semantic correctness; `novalidate` makes it non-enforced by the browser but it still signals field intent to AT.
- `aria-describedby="email-error"` — FR-014, NFR-004: links the input to the error hint span so screen readers read hint text as part of the field's accessible description.
- `aria-invalid="false"` — FR-013, NFR-004: initial value; JS updates this to `"true"` on invalid and back to `"false"` on valid or neutral.
- `<span id="email-icon" class="field-icon" aria-hidden="true">` — FR-011, FR-012, DD-03: the icon character (⚠ or ✓) is set at runtime by JS. `aria-hidden="true"` marks the glyph as decorative (NFR-006); semantic meaning is conveyed through `aria-invalid` and `aria-describedby`. The `id` attribute is used by `document.getElementById('email-icon')` in TASK-004 (DD-03: immune to adjacent-sibling selector fragility).
- `<span id="email-error" class="error-hint" role="status">` — FR-014, NFR-004, FU-05/L-003: `role="status"` implicitly carries `aria-live="polite"` and `aria-atomic="true"` per the ARIA specification. The explicit `aria-live="polite"` attribute is intentionally omitted (L-003) to avoid potential double-announcement in older NVDA/JAWS versions.
- `<div class="input-wrapper">` — FR-012: required ancestor for CSS `position: relative` so the icon span can be positioned absolutely at the right edge of the input. (CSS `::after` pseudo-elements cannot be rendered on `<input>` replaced elements.)

The password field at the original line 64 is not modified. Its `input:focus` styling will be provided by the CSS rule added in TASK-003 which targets all `<input>` elements.

**Definition of done / Acceptance test:**

1. View source of the rendered page and confirm the form tag contains `novalidate`.
2. Confirm the username input has `type="email"`, `name="username"`, `id="email"`, `placeholder="Email"`, `aria-describedby="email-error"`, `aria-invalid="false"`.
3. Confirm `<span id="email-icon" class="field-icon" aria-hidden="true">` is present inside the `.input-wrapper` div.
4. Confirm `<span id="email-error" class="error-hint" role="status">` is present immediately after the `.input-wrapper` div, with no `aria-live` attribute.
5. Confirm the password `<input type="password">` is structurally unchanged (no wrapper div, no aria attributes added).
6. Open the browser DevTools accessibility tree and confirm the email input reports `aria-invalid: false` and `aria-describedby` pointing to the `email-error` element.

---

### TASK-003 — Add CSS validation and focus styles in login.html

| Field | Value |
|---|---|
| Task ID | TASK-003 |
| Workstream | Frontend |
| Owner role | Frontend Engineer |
| Complexity | S |
| Dependencies | TASK-002 |
| Requirement coverage | FR-005, FR-006, FR-007, FR-008, FR-010, FR-011, FR-016, NFR-001, NFR-003, NFR-005, NFR-007, DD-05, DD-06, L-001, AC-1, AC-2, AC-3 |

**File to change:** `templates/login.html`

**Exact change description:**

Inside the `<style>` block, immediately after the existing `.error { ... }` rule (which ends at line 50 of the current file), append the following new rules in the exact order shown. Declaration order is load-bearing: `input:focus` must appear before `input.invalid` and `input.valid` so that when both a pseudo-class and a class are active on the same element, the validation border color wins by CSS source-order precedence (equal specificity (0,1,1) — last declared rule wins per DD-05).

```css
        /* Wrapper positions the icon span relative to the input boundary */
        .input-wrapper {
            position: relative;
            display: block;
            margin: 0.4rem 0;
        }
        .input-wrapper input {
            margin: 0;
            width: 100%;
            box-sizing: border-box;
        }
        /* Icon span: absolutely positioned at right edge, hidden until JS shows it */
        .field-icon {
            position: absolute;
            right: 0.6rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.9rem;
            pointer-events: none;
            display: none;
        }
        /* Focus state — MUST be declared before .invalid and .valid rules */
        input:focus {
            border-color: #1877f2;
            outline: none;
            box-shadow: 0 0 0 3px rgba(24, 119, 242, 0.2);
        }
        /* Validation states — declared after :focus so they win when both active (DD-05) */
        input.invalid { border-color: #d32f2f; padding-right: 2rem; }
        input.valid   { border-color: #2e7d32; padding-right: 2rem; }
        /* Error hint text below email field */
        .error-hint {
            display: block;
            font-size: 0.75rem;
            color: #d32f2f;
            min-height: 1em;
            margin-top: 0.15rem;
        }
        /* Smooth transition only for users who have not opted into reduced motion (L-001) */
        @media (prefers-reduced-motion: no-preference) {
            input { transition: border-color 0.12s ease; }
        }
```

Rule-by-rule rationale:

- `.input-wrapper`: Sets `position: relative` to create the containing block for the absolutely positioned icon span. Sets `margin: 0.4rem 0` to preserve the spacing the original `input` rule provided (the `.input-wrapper input` override below sets `margin: 0` to prevent double spacing).
- `.input-wrapper input`: Overrides `margin` to `0` since the wrapper now owns vertical spacing. `width: 100%` and `box-sizing: border-box` are already on the base `input` rule but are restated explicitly to be safe against future CSS refactors.
- `.field-icon`: `position: absolute; right: 0.6rem; top: 50%; transform: translateY(-50%)` centers the icon vertically and places it at the right inner edge. `pointer-events: none` prevents the icon from interfering with mouse clicks on the input. `display: none` hides it by default; JS sets `display: block` when a state is active.
- `input:focus`: `border-color: #1877f2` (DD-06 — brand blue with 4.3:1 contrast on white, exceeds WCAG SC 1.4.11 3:1 minimum). `outline: none` suppresses the default browser focus ring, replaced by the `box-shadow` ring (FR-008, NFR-005). The `box-shadow: 0 0 0 3px rgba(24,119,242,0.2)` provides the accessible keyboard focus indicator. When the field is focused AND has `.invalid` or `.valid`, this box-shadow still renders alongside the validation border color — this dual-signal appearance is intentional (DD-05) and must not be removed.
- `input.invalid`: `border-color: #d32f2f` — FR-010. `padding-right: 2rem` pushes typed text left to prevent overlap with the icon (FR-011).
- `input.valid`: `border-color: #2e7d32` — FR-016. Same `padding-right: 2rem` for icon clearance (FR-017). Both `#d32f2f` and `#2e7d32` provide approximately 4.8:1 and 4.7:1 contrast on white respectively — both exceed the WCAG 3:1 minimum for NFR-007.
- `.error-hint`: `min-height: 1em` prevents layout shift when the hint text appears/disappears (the space is reserved even when the span is empty).
- `@media (prefers-reduced-motion: no-preference)`: The `transition: border-color 0.12s ease` is gated behind this media query so users who have enabled reduced-motion OS preferences do not receive any animation (L-001, FU-03). The 0.12s duration is within the 0.15s ceiling permitted by NFR-001.

**Definition of done / Acceptance test:**

1. Open the login page in Chrome and tab into the email field — border must turn blue (`#1877f2`) with a visible box-shadow ring. Tab into the password field — same blue border must appear.
2. Open DevTools > Elements, select the email input, confirm `input:focus` applies `border-color: #1877f2` and `box-shadow` in computed styles.
3. Add class `invalid` to the email input in DevTools and confirm border turns red, `padding-right` increases to `2rem`, and the class `.field-icon` position is correct (icon would appear at right edge).
4. Add class `valid` instead and confirm border turns green with same `padding-right`.
5. Confirm that when `.invalid` is active AND the input is focused, the blue box-shadow is still visible alongside the red border (dual signal).
6. Confirm `.error-hint` has `min-height: 1em` in computed styles (layout space reserved when empty).
7. In a browser with reduced-motion preference enabled (OS setting or DevTools emulation), confirm no border transition animation occurs.

---

### TASK-004 — Add JavaScript validation state machine in login.html

| Field | Value |
|---|---|
| Task ID | TASK-004 |
| Workstream | Frontend |
| Owner role | Frontend Engineer |
| Complexity | M |
| Dependencies | TASK-002, TASK-003 |
| Requirement coverage | FR-009, FR-013, FR-014, FR-015, FR-017, FR-018, FR-019, FR-020, NFR-001, NFR-002, NFR-003, NFR-004, NFR-006, DD-02, DD-04, AC-2, AC-3, AC-4 |

**File to change:** `templates/login.html`

**Exact change description:**

Immediately before the closing `</body>` tag (currently line 68), insert the following `<script>` block. Do not place it in the `<head>` — it must follow the DOM elements it references so `getElementById` calls return non-null without needing `DOMContentLoaded`.

```html
    <script>
        var emailInput = document.getElementById('email');
        var emailIcon  = document.getElementById('email-icon');
        var emailError = document.getElementById('email-error');

        function validateEmail() {
            var value = emailInput.value;
            if (value === '') {
                emailInput.classList.remove('invalid', 'valid');
                emailInput.setAttribute('aria-invalid', 'false');
                emailIcon.style.display = 'none';
                emailIcon.textContent = '';
                emailError.textContent = '';
            } else if (!emailInput.validity.valid) {
                emailInput.classList.remove('valid');
                emailInput.classList.add('invalid');
                emailInput.setAttribute('aria-invalid', 'true');
                emailIcon.textContent = '⚠︎';
                emailIcon.style.color = '#d32f2f';
                emailIcon.style.display = 'block';
                emailError.textContent = 'Please enter a valid email address.';
            } else {
                emailInput.classList.remove('invalid');
                emailInput.classList.add('valid');
                emailInput.setAttribute('aria-invalid', 'false');
                emailIcon.textContent = '✓';
                emailIcon.style.color = '#2e7d32';
                emailIcon.style.display = 'block';
                emailError.textContent = '';
            }
        }

        if (emailInput) {
            emailInput.addEventListener('input', validateEmail);
            emailInput.addEventListener('blur',  validateEmail);
        }
    </script>
```

Line-by-line rationale:

- `document.getElementById('email')` / `'email-icon'` / `'email-error'` — DD-03: id-based lookup is explicit, O(1), and immune to silent null returns from fragile adjacent-sibling CSS selectors. All three IDs were added in TASK-002.
- `var` is used instead of `const`/`let` to maximize compatibility with the broadest browser range for this inline context. Either is fine in target browsers (NFR-008), but `var` avoids any TDZ edge case.
- **Neutral branch (`value === ''`)**: Removes both `.invalid` and `.valid` classes in one call, sets `aria-invalid` to `"false"`, hides and empties the icon, clears the hint. This covers FR-019 (neutral on empty) and FR-020 (re-enter neutral when user clears all characters).
- **Invalid branch (`!emailInput.validity.valid`)**: Removes `.valid` before adding `.invalid` to ensure both classes are never active simultaneously. Sets `aria-invalid="true"` (FR-013). Sets icon `textContent` to `'⚠︎'` — this is U+26A0 WARNING SIGN followed immediately by U+FE0E VARIATION SELECTOR-15 (DD-02, M-001 fix). The variation selector forces text/monochrome presentation on iOS, macOS, and Windows font stacks that would otherwise render the ⚠ glyph as a color emoji bitmap, which CSS `color` cannot tint. Without the variation selector, the icon would appear yellow/orange rather than the specified red on those platforms (NFR-003 would fail). `'✓'` CHECK MARK used in the valid branch does not have an emoji variant and requires no variation selector. Sets hint text to the exact string "Please enter a valid email address." (FR-014).
- **Valid branch**: Removes `.invalid`, adds `.valid`, sets `aria-invalid="false"` (FR-018), sets icon to `'✓'` in green (FR-017), clears hint text (FR-018).
- **Null guard `if (emailInput)`** (DD-04): If `document.getElementById('email')` returns null due to a template rendering error or future HTML rename, the event listeners are not attached and no TypeError is thrown. The page remains fully usable without inline validation; the server-side credential check is the functional backstop. The `validateEmail` function is defined outside the guard because it is only ever called from within the guarded `addEventListener` calls — it cannot be invoked if `emailInput` is null.
- `addEventListener('input', validateEmail)` — FR-009: fires on every keystroke and character deletion so users receive feedback during typing.
- `addEventListener('blur', validateEmail)` — A-03: fires when the field loses focus, so users who paste a complete address without typing individual characters also receive feedback on tab-out.
- No `async`, `await`, `setTimeout`, `fetch`, `XMLHttpRequest`, `eval`, or `new Function` calls appear anywhere. NFR-002 is fully satisfied.

**State machine behavior summary:**

| Current value | `validity.valid` | Resulting state | Classes active | `aria-invalid` | Icon | Hint text |
|---|---|---|---|---|---|---|
| `""` (empty) | — | Neutral | none | `"false"` | hidden, `""` | `""` |
| Non-empty | `false` | Invalid | `.invalid` | `"true"` | ⚠ red (`#d32f2f`) | "Please enter a valid email address." |
| Non-empty | `true` | Valid | `.valid` | `"false"` | ✓ green (`#2e7d32`) | `""` |

All three states are reachable from any other state on a single `input` or `blur` event.

**Definition of done / Acceptance test:**

1. Load the login page, type `notanemail` into the email field — confirm red border appears, red ⚠ icon appears at right edge (not overlapping text), and hint "Please enter a valid email address." appears below the field. Confirm `aria-invalid` attribute on the input is `"true"` in DevTools.
2. Continue typing to form `notanemail@example.com` — confirm border changes to green, ⚠ icon is replaced by ✓ in green, hint text is cleared. Confirm `aria-invalid` is `"false"`.
3. Delete all text — confirm border returns to neutral gray, icon disappears, no hint text. Confirm `aria-invalid` is `"false"`.
4. Paste `admin@example.com` into the field then tab away — confirm green border and ✓ icon appear on blur (not just on keystroke).
5. On iOS Safari or macOS Safari: confirm the ⚠ icon is red (not yellow/orange). If testing environment lacks a real device, inspect the `textContent` of `#email-icon` in DevTools and confirm it contains two characters: U+26A0 and U+FE0E.
6. Disable JavaScript in the browser, load the page, fill in any value, click Log In — confirm the form submits (is not blocked by JS). The server will return a flash error for wrong credentials; this confirms NFR-012/graceful degradation behavior.
7. Open the browser console and confirm no JavaScript errors are present on page load or during validation interactions.

---

### TASK-005 — Create README.md with demo credential and setup instructions

| Field | Value |
|---|---|
| Task ID | TASK-005 |
| Workstream | Documentation |
| Owner role | Frontend Engineer or any developer |
| Complexity | XS |
| Dependencies | TASK-001 |
| Requirement coverage | DIR-003, L-004, FU-04, AC-5 |

**File to change:** `README.md` (new file — does not currently exist in the project root)

**Exact change description:**

Create a new file at `C:\Users\VishnukumarDhanaraja\Claude\SessionTwo\LoginApplication\README.md` with at minimum the following content:

```markdown
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
```

The credential documents the value confirmed in TASK-001 (`admin@example.com` / `password123`), satisfying DIR-003.

**Definition of done / Acceptance test:**

1. Confirm the file `README.md` exists at the project root.
2. Confirm it contains the email `admin@example.com` and the password `password123`.
3. Confirm it includes instructions for setting `SECRET_KEY` as an environment variable.
4. A new developer following only the README should be able to start the server and log in successfully without reading any other file.

---

### TASK-006 — End-to-end verification

| Field | Value |
|---|---|
| Task ID | TASK-006 |
| Workstream | QA / Verification |
| Owner role | QA Engineer or implementing developer |
| Complexity | S |
| Dependencies | TASK-001, TASK-002, TASK-003, TASK-004, TASK-005 |
| Requirement coverage | AC-1, AC-2, AC-3, AC-4, AC-5 — all functional and non-functional requirements |

**Files reviewed (not changed):** All project files in their final state.

**Exact change description:**

No code changes. Execute the full verification checklist in Section 10 of this plan. Record pass/fail for each AC step. All steps must pass before the feature is marked complete.

**Definition of done / Acceptance test:**

Every item in the Verification Checklist (Section 10) is checked off and confirmed passing. No JavaScript console errors. The line count of new CSS and JavaScript lines added to `login.html` does not exceed 80 (NFR-011).

---

## 4. Dependency Graph

```
TASK-001 (app.py credential)
    |
    +-----------------------> TASK-005 (README)
    |                              |
    |                              |
TASK-002 (HTML structure)          |
    |                              |
    +---> TASK-003 (CSS)           |
              |                    |
              +---> TASK-004 (JS)  |
                        |          |
                        |          |
                        +----------+----------> TASK-006 (verification)
```

Parallel execution: TASK-001 and TASK-002 have no mutual dependency and may be executed concurrently by different contributors.

---

## 5. Blocked Tasks List

| Blocked task | Blocked by | Reason |
|---|---|---|
| TASK-003 | TASK-002 | CSS selectors `.input-wrapper`, `.field-icon`, `input.invalid`, `input.valid`, `.error-hint` reference class names and elements introduced in TASK-002. Writing CSS before the HTML exists risks selector drift if element names change. |
| TASK-004 | TASK-002 | JavaScript `getElementById('email')`, `getElementById('email-icon')`, `getElementById('email-error')` reference IDs added in TASK-002. If TASK-002 is not complete, all three references return null and event listeners are never attached. |
| TASK-004 | TASK-003 | JavaScript toggles `classList.add('invalid')`, `classList.add('valid')`. If TASK-003 is not complete, these class names have no corresponding CSS rules, so visual state changes will not appear even though the DOM mutations occur. |
| TASK-005 | TASK-001 | README documents the email credential value. If TASK-001 has not been made, the credential value in app.py is still `"admin"` and the README would document an incorrect value. |
| TASK-006 | TASK-001, TASK-002, TASK-003, TASK-004, TASK-005 | Full AC verification requires all code and documentation changes to be in place. Verifying any AC before all tasks are complete will produce false negatives (AC-5 requires the credential from TASK-001; AC-1/2/3/4 require HTML, CSS, and JS from TASK-002/003/004). |

---

## 6. Milestone Outcomes

| Milestone | Tasks complete | Deliverable state |
|---|---|---|
| M1 — Backend ready | TASK-001 | `app.py` accepts `admin@example.com` credentials. End-to-end login can be tested via curl. |
| M2 — HTML scaffolded | TASK-002 | Email input is `type="email"`, wrapped, has IDs, has ARIA attributes. Form has `novalidate`. Page renders without visual changes yet (CSS and JS not yet added). |
| M3 — Visual states active | TASK-003 | Blue focus ring on both fields, red/green borders on email field classes, icon positioning active. States are testable by manually adding/removing classes in DevTools. |
| M4 — Validation live | TASK-004 | Full interactive validation works end-to-end in the browser. All five ACs are testable. |
| M5 — Feature complete | TASK-005, TASK-006 | README documents credential. All AC checks pass. NFR-011 line count confirmed. Feature is ready for QA sign-off. |

---

## 7. Critical Path and Sequencing Risks

### Critical path

```
TASK-002 → TASK-003 → TASK-004 → TASK-006
```

This is the longest dependency chain and drives the delivery schedule. TASK-001 and TASK-005 are off the critical path and can be completed at any point before TASK-006.

### Sequencing risks

| Risk | Impact | Mitigation |
|---|---|---|
| Developer writes TASK-003 and TASK-004 together in a single edit without completing TASK-002 first | CSS class names or element IDs may be mistyped or inconsistent with the HTML introduced in TASK-002, causing silent failures (wrong selector, getElementById returns null caught by null guard) | Verify the HTML structure of TASK-002 in the browser before beginning TASK-003. |
| CSS source order is reversed — `.invalid`/`.valid` rules placed before `input:focus` in the stylesheet | Validation border color loses to focus blue when both are active (FR-007 broken) | The implementation notes in Section 9 call this out explicitly. CSS rules must be added in the exact order shown in TASK-003. |
| `aria-live="polite"` is added to the `#email-error` span (pattern familiar from other projects) | Some NVDA/JAWS versions double-announce state changes when both `role="status"` implicit live region and an explicit `aria-live` attribute are present | TASK-002 description explicitly states no `aria-live` attribute. L-003/FU-05 note is repeated in the implementation notes below. |
| U+FE0E variation selector omitted from the warning icon assignment | ⚠ renders as a color emoji on iOS/macOS/Windows; CSS color has no effect on the glyph; icon appears yellow/orange not red (NFR-003 broken) | TASK-004 specifies the exact Unicode escape `'⚠︎'`. DD-02 and M-001 are repeated in implementation notes. |
| NFR-011 line count exceeded | NFR non-compliance | Developer must count lines before committing. Architecture estimates ~71 lines; budget is 80. Comments in CSS/JS should be minimal inline notes, not multi-line block comments. |

---

## 8. Workstream Summary Table

| Task ID | Title | Workstream | Owner | Effort | Dependencies | Requirement IDs |
|---|---|---|---|---|---|---|
| TASK-001 | Update demo credential in app.py | Backend | Backend Engineer | XS | — | FR-004, DIR-002, DIR-003, AC-5 |
| TASK-002 | Update HTML input structure in login.html | Frontend | Frontend Engineer | S | — | FR-001, FR-002, FR-003, DD-01, DD-03, DD-05, L-003, NFR-004, NFR-006, DIR-001 |
| TASK-003 | Add CSS validation and focus styles in login.html | Frontend | Frontend Engineer | S | TASK-002 | FR-005–FR-008, FR-010, FR-011, FR-016, NFR-001, NFR-005, NFR-007, DD-05, DD-06, L-001 |
| TASK-004 | Add JavaScript validation state machine in login.html | Frontend | Frontend Engineer | M | TASK-002, TASK-003 | FR-009, FR-013–FR-020, NFR-001–NFR-004, NFR-006, DD-02, DD-04 |
| TASK-005 | Create README.md with demo credential and setup instructions | Documentation | Any developer | XS | TASK-001 | DIR-003, L-004 |
| TASK-006 | End-to-end verification | QA | QA Engineer | S | TASK-001–TASK-005 | All ACs |

---

## 9. Implementation Notes

### Design Decisions (DD-01 through DD-07) — mandatory implementation constraints

**DD-01 — Add `novalidate` to the `<form>` element.**
The `novalidate` attribute must be present on the form tag. Without it, the browser renders a native tooltip balloon on submit for invalid email values. This tooltip is styled inconsistently across browsers, is not integrated with the custom icon/hint UI, and causes double-announcement for screen reader users (both the native popup and `aria-invalid` fire). With `novalidate`, JavaScript owns all validation feedback. The server's credential check is the security gate; blank submissions are rejected by the server with a flash message. This decision supersedes the native-validation fallback clause in NFR-012 (design review H-001, resolved).

**DD-02 — Warning icon must use U+26A0 + U+FE0E text variation selector.**
When setting the warning icon character in JavaScript, always use `'⚠︎'` (not `'⚠'` alone and not the literal `⚠` character). U+26A0 has emoji presentation by default on iOS, macOS, and many Windows configurations. In emoji presentation, the glyph is rendered as a color bitmap and CSS `color` has no effect — the icon appears yellow/orange, not the required red (#d32f2f), breaking NFR-003. The text variation selector U+FE0E forces monochrome text glyph rendering so CSS color applies correctly. U+2713 CHECK MARK (`'✓'`) used for the valid state does not have an emoji variant and requires no variation selector.

**DD-03 — Use `id="email-icon"` on the icon span; select with `getElementById`.**
The icon span must carry `id="email-icon"`. JavaScript must reference it via `document.getElementById('email-icon')`, not via `querySelector('#email + .field-icon')` or any CSS adjacent-sibling combinator. The sibling selector silently returns `null` if any element is ever inserted between the input and the icon span in a future HTML edit. The id-based lookup is explicit, O(1), and immune to such structural changes.

**DD-04 — Wrap event listener registration in a null guard.**
The event listeners must be registered inside `if (emailInput) { ... }`. If `document.getElementById('email')` returns null (template rendering error, future id rename), the null guard prevents a TypeError from throwing and blocking page usability. The `validateEmail` function definition is placed outside the guard because it is only called from the guarded event listeners — it cannot be invoked if `emailInput` is null.

**DD-05 — Dual visual signal (blue box-shadow + validation border) is intentional when a validated field is focused.**
When the email input is focused AND has the `.invalid` or `.valid` class, two CSS rules apply simultaneously: `input:focus` provides the blue box-shadow ring; `input.invalid`/`input.valid` provides the red/green border color (and wins by source-order precedence at equal specificity). The blue box-shadow ring is the accessible keyboard focus indicator required by NFR-005. Do not add `box-shadow: none` to `.invalid` or `.valid` rules — this dual signal must be preserved.

**DD-06 — Accept `#1877f2` for the focus border color.**
`#1877f2` is the same blue used on the submit button (existing brand color). It provides approximately 4.3:1 contrast on white, exceeding the WCAG SC 1.4.11 3:1 minimum for non-text contrast. Formal designer sign-off was not obtained before review; the decision is accepted with this documented rationale (OQ-02 closed as accepted risk). If a designer later specifies a different shade, update only the `border-color` in `input:focus` and the `rgba()` value in `box-shadow` — no other lines change.

**DD-07 — The USERS dict key update in `app.py` is the sole backend change.**
`request.form.get("username")` in the `/login` route is not modified. The form still submits `name="username"` as the POST field. The dict key change from `"admin"` to `"admin@example.com"` is the only permitted `app.py` modification. Route logic, session management, flash messages, and all other routes are untouched.

---

### Follow-up items and low-severity findings from design review

**FU-01 (I-002) — Add `<label>` elements for both form fields.**
Neither field currently has a `<label>` element. Placeholders are not a WCAG-compliant substitute for labels (they disappear when the user types). This is a pre-existing issue not introduced by this story. Adding visible labels is a separate accessibility story and is out of scope here. Track as a follow-up.

**FU-02 (I-001) — Resolve pre-existing XSS in the dashboard route.**
`app.py` line 59 interpolates `session['user']` directly into an HTML string without escaping. This is a pre-existing vulnerability that is harmless for the current hardcoded USERS dict but would become exploitable if USERS were ever extended with user-supplied data or replaced with a database. Use `render_template()` with a Jinja2 template for the dashboard in a follow-up story.

**FU-03 (L-001) — `prefers-reduced-motion` media query is incorporated in this story.**
The CSS transition rule must be wrapped in `@media (prefers-reduced-motion: no-preference)` as specified in TASK-003. This applies to this story, not a future one.

**FU-04 (L-004) — README.md must be created in this story.**
DIR-003 requires the updated credential to be documented. TASK-005 in this plan addresses this directly.

**FU-05 (L-003) — Do NOT add `aria-live="polite"` to the `#email-error` span.**
`role="status"` already implies `aria-live="polite"` and `aria-atomic="true"` per the ARIA specification. Adding an explicit `aria-live="polite"` attribute is redundant and may cause double-announcement in older NVDA/JAWS versions. The HTML in TASK-002 intentionally omits `aria-live`.

---

### Implementation pitfalls to avoid

1. **Do not add `id="email"` to the password field.** The JavaScript targets `id="email"` specifically. The password field must remain without an id (or with a different id). Adding `id="email"` to the password input would cause the JS to bind validation to the wrong field.

2. **Do not change `name="password"` or `name="username"` on either input.** The Flask route reads these exact POST field names. Any rename breaks authentication without a corresponding backend change (which is out of scope per DIR-002).

3. **Do not add the `.invalid` or `.valid` class statically in HTML.** Both classes must be absent on page load. JS adds them dynamically. Starting with a class present would cause validation styling to appear on the untouched field at page load.

4. **Do not place the `<script>` block in `<head>`.** The script references `getElementById` calls that rely on the DOM being fully rendered. Place the `<script>` block immediately before `</body>`. Do not wrap in `DOMContentLoaded` (it is unnecessary if the script is at the end of body and adds a line toward the NFR-011 budget).

5. **Do not reorder CSS rules.** The `input:focus` rule must appear in the stylesheet before `input.invalid` and `input.valid`. If the order is reversed, the blue focus border overrides the red/green validation border when the user is typing (both `:focus` and the validation class are active simultaneously), breaking FR-007.

6. **Do not add `box-shadow: none` to `.invalid` or `.valid` rules.** This would eliminate the keyboard focus ring when a validated field is focused, violating NFR-005. The dual-signal appearance (blue ring + validation border) is correct per DD-05.

7. **Do not use `innerHTML` in the JavaScript block.** All DOM writes must use `textContent` (for icon and hint text) and `setAttribute`/`classList` (for ARIA and class changes). `innerHTML` creates an XSS risk if any user-typed content were ever passed to it; `textContent` treats its argument as a plain string.

8. **Count the NFR-011 line budget before committing.** New CSS and JS lines combined must not exceed 80. The architecture estimates ~71. If the count approaches 80, inline comments are the first thing to trim. Single-line CSS declarations (e.g., `input.invalid { border-color: #d32f2f; padding-right: 2rem; }`) are acceptable and reduce the count.

9. **Test the ⚠ icon color on Safari (macOS or iOS) specifically.** This is where U+26A0 emoji rendering is most likely to occur. If the icon appears yellow/orange rather than red, the variation selector `︎` is missing or was lost during a copy-paste.

10. **Verify the SECRET_KEY environment variable is set before running the server.** `app.py` raises a RuntimeError at startup if `SECRET_KEY` is absent. The README created in TASK-005 provides setup instructions, but the developer must have the variable set locally before running acceptance tests.

---

## 10. Verification Checklist

Execute all steps manually after TASK-001 through TASK-005 are complete. All steps must pass before the feature is accepted.

---

### AC-1 — Focus State (Both Fields)

*Given I click or tap inside an input field, when the field is active, then the border must change to blue.*

- [ ] AC-1.1: Click into the email field. Confirm border changes from gray (`#ccc`) to blue (`#1877f2`). The blue box-shadow ring is also visible.
- [ ] AC-1.2: Click away from the email field. Confirm border returns to gray.
- [ ] AC-1.3: Click into the password field. Confirm border changes to the same blue. The password field must not show any icon or hint text.
- [ ] AC-1.4: Click away from the password field. Confirm border returns to gray.
- [ ] AC-1.5: Tab through the form fields using only the keyboard. Confirm both fields show a visible blue focus ring (box-shadow) when keyboard-focused. Confirm focus ring is not suppressed (`outline: none` is replaced by the box-shadow).
- [ ] AC-1.6: With the email field in `.valid` state, tab into it. Confirm green border is visible (validation wins over focus blue border per source order) AND the blue box-shadow ring is also visible alongside the green border (DD-05 dual signal).

---

### AC-2 — Invalid Email State

*Given I am typing my email address, when I enter an invalid format, then the border turns red and a warning icon appears.*

- [ ] AC-2.1: Type `notanemail` into the email field. Confirm border turns red while typing (not only on blur).
- [ ] AC-2.2: Confirm the ⚠ icon appears at the right edge of the email field. Confirm the icon does not overlap with the typed text.
- [ ] AC-2.3: Open DevTools > Elements. Confirm `aria-invalid` on the email input is `"true"`.
- [ ] AC-2.4: Confirm the hint text "Please enter a valid email address." appears below the email field.
- [ ] AC-2.5: Open the browser console. Confirm no JavaScript errors are present.
- [ ] AC-2.6 (Accessibility): Use a screen reader (or DevTools accessibility inspector) and confirm the hint text is announced when the invalid state is entered (role="status" live region).
- [ ] AC-2.7 (Emoji check): If testing on Safari (macOS or iOS), confirm the ⚠ icon is red, not yellow or orange.
- [ ] AC-2.8: Tab away from the invalid email field and back again (blur then focus). Confirm the invalid state persists and the icon remains visible.

---

### AC-3 — Valid Email State

*Given I correct my email to a valid format, then the red indicators disappear and a green checkmark appears.*

- [ ] AC-3.1: Starting from the invalid state in AC-2.1, continue typing to complete `notanemail@example.com`. Confirm the red border is immediately replaced by a green border.
- [ ] AC-3.2: Confirm the ⚠ icon is replaced by ✓ in green.
- [ ] AC-3.3: Confirm the hint text is cleared (empty span remains but contains no text).
- [ ] AC-3.4: Open DevTools > Elements. Confirm `aria-invalid` on the email input is `"false"`.
- [ ] AC-3.5: Clear the field and paste `admin@example.com` in one action. Tab away. Confirm the valid state (green border, ✓ icon) appears on blur.

---

### AC-4 — Neutral State on Empty Field

*Given the email field is empty, neither red nor green styling is shown.*

- [ ] AC-4.1: Load the login page. Confirm the email field shows a neutral gray border with no icon and no hint text.
- [ ] AC-4.2: Type a valid email (`admin@example.com`). Confirm green state. Then delete all characters one by one. Confirm the field returns to neutral gray border with no icon and no hint text when the last character is deleted.
- [ ] AC-4.3: Reach the invalid state (type `bad`). Then select all and delete. Confirm neutral state is restored.
- [ ] AC-4.4: Confirm that clearing the field removes the `.invalid` and `.valid` classes (DevTools Elements panel).

---

### AC-5 — Backend Compatibility

*Given the form is submitted with the updated demo credential, then login must succeed.*

- [ ] AC-5.1: Open `app.py` and confirm line 25 reads `"admin@example.com": "password123"`.
- [ ] AC-5.2: Start the Flask server (`SECRET_KEY` must be set in the environment).
- [ ] AC-5.3: Navigate to `http://127.0.0.1:5000/login`.
- [ ] AC-5.4: Enter `admin@example.com` in the email field and `password123` in the password field.
- [ ] AC-5.5: Click Log In. Confirm the browser redirects to `/dashboard` and the dashboard page displays `Welcome, admin@example.com!`.
- [ ] AC-5.6: Enter `admin` (old credential key) in the email field and `password123`. Click Log In. Confirm login fails with the flash message "Invalid username or password." (validates that the old credential no longer works).
- [ ] AC-5.7: Enter a correctly formatted but non-existent email (`user@test.com`) and `password123`. Click Log In. Confirm login fails with the flash message.
- [ ] AC-5.8: Confirm the `name="username"` attribute is present on the email input in the rendered HTML source (DIR-001 contract).

---

### NFR-011 Line Count Check

- [ ] Count the total number of new lines added to `login.html` that are CSS or JavaScript (exclude blank lines if preferred, but be consistent). The total must be 80 or fewer.

---

*End of Implementation Plan*
