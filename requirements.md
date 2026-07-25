# Requirements Specification

**Project:** Flask Login Application  
**Feature:** UI Enhancement — Field-Level Visual Validation and Focus States  
**Author:** Requirements Collaboration Agent  
**Date:** 2026-07-25  
**Status:** Draft for Review

---

## 1. Story Summary

As a user logging into my account, I want the input fields to give me instant visual feedback as I interact with them, so that I know my inputs are correct and active before I even click the login button.

Key points:

- The current `username` text input must be repurposed as an email input (`type="email"`) to enable format validation.
- Both the email field and the password field must display a blue border when focused (AC1).
- The email field must display a red border and a red warning icon when the entered value is not a valid email format (AC2).
- The email field must replace those red indicators with a green checkmark icon when the value is a valid email format (AC3).
- The password field requires focus-state styling only; it has no inline validation requirement.
- All validation logic must be implemented as client-side JavaScript inside `templates/login.html`. No changes to backend route logic are required.
- The backend demo credential key must be updated from `"admin"` to a valid email address so the demo workflow remains functional after the field type change.

---

## 2. Assumptions

| ID   | Assumption |
|------|-----------|
| A-01 | The email field will use `name="username"` so the existing backend route (`request.form.get("username")`) requires no code changes. |
| A-02 | The USERS demo credential key in `app.py` will be updated from `"admin"` to `"admin@example.com"` to produce a valid email that passes client-side validation. The password remains `"password123"`. |
| A-03 | Validation is triggered on the `input` event (as the user types) and also on the `blur` event (when the field loses focus), so users receive feedback during typing and after leaving the field. |
| A-04 | The HTML5 `input.validity.valid` API is used to determine email format validity, consistent with browser-native email validation rules. No third-party library is introduced. |
| A-05 | Icons (warning and checkmark) are rendered using inline Unicode characters or inline SVG positioned with CSS inside the input field using `padding-right` and absolute-positioned pseudo-elements or wrapper elements, with no external asset requests. |
| A-06 | If JavaScript is disabled, the browser's native HTML5 email validation (triggered on form submit) remains the fallback. The form must remain submittable in a no-JS environment. |
| A-07 | Target browsers are the two most recent stable releases of Chrome, Firefox, Safari, and Microsoft Edge at the time of implementation. |
| A-08 | No CSS framework or external stylesheet is introduced. All new styles are added inline within the `<style>` block in `login.html`. |
| A-09 | The `required` attribute is retained on both fields. The login button does not become disabled based on validation state; the form submission itself is the enforcement point. |

---

## 3. In Scope

- Changing the username field to `type="email"` while retaining `name="username"`.
- Focus-state blue border styling for both the email field and the password field.
- Invalid-state red border and red warning icon for the email field.
- Valid-state green checkmark icon and removal of red indicators for the email field.
- JavaScript validation logic added inline within `templates/login.html`.
- Update to the USERS demo credential in `app.py` (key change only: `"admin"` to `"admin@example.com"`).
- ARIA attribute support (`aria-invalid`, `aria-describedby`) on the email field for screen reader compatibility.
- Updating the placeholder text of the email field from "Username" to "Email".

---

## 4. Out of Scope

- Server-side email validation or any other backend route changes beyond the USERS dict key update.
- Password field inline validation (strength indicator, match confirmation, or format rules).
- Real-time username availability or account existence checks.
- Remember me / persistent login functionality.
- Multi-factor authentication.
- Any change to the dashboard or logout routes.
- Introduction of a CSS framework or JavaScript library.
- Internationalisation or localisation of validation messages.
- Custom domain or MX record verification for the email address.
- Changes to the flash message system for server-side login errors.

---

## 5. Functional Requirements

### 5.1 Field Identity and HTML Structure

**FR-001** — The username input field in `login.html` must be changed from `type="text"` to `type="email"`.

**FR-002** — The email field must retain `name="username"` so that the form POST payload key is unchanged and the backend `request.form.get("username")` call continues to work without modification.

**FR-003** — The placeholder text of the email field must be updated from "Username" to "Email".

**FR-004** — The demo user credential key in `app.py` must be updated from `"admin"` to `"admin@example.com"`. The password value `"password123"` is unchanged. No other lines in `app.py` are modified.

### 5.2 Focus State (Applies to Both Fields)

**FR-005** — When the email field receives focus (via click, tap, or keyboard tab), its border must change to a distinct blue color. The exact color must be `#1877f2` (the existing brand blue used on the submit button) or a visually equivalent accessible blue with a contrast ratio of at least 3:1 against the white field background as required by WCAG 2.1 SC 1.4.11.

**FR-006** — When the password field receives focus (via click, tap, or keyboard tab), its border must change to the same distinct blue color defined in FR-005.

**FR-007** — When a focused field loses focus (blur), the border must return to its default neutral state (`#ccc`) unless the email field is in a validation state (invalid or valid), in which case the validation-state border color takes precedence.

**FR-008** — The focus-state border style must be implemented using a CSS `:focus` rule. JavaScript is not required solely for focus styling.

### 5.3 Email Field — Invalid State

**FR-009** — While the user is typing in the email field, the system must evaluate the input value on every `input` event using the HTML5 Constraint Validation API (`element.validity.valid`).

**FR-010** — If the email field contains a non-empty value that fails the email format check (e.g., missing `@`, missing domain, incomplete TLD), the field border must change to red (`#d32f2f` or equivalent accessible red).

**FR-011** — When the invalid state is active, a red warning icon must appear visually inside the right edge of the email input field. The icon must be a recognized warning symbol (e.g., Unicode `⚠` WARNING SIGN, or an inline SVG exclamation triangle). The icon must not overlap with the typed text under normal field widths.

**FR-012** — The warning icon must not be implemented as a background image requiring an external HTTP request. It must be rendered either via CSS `content` with a pseudo-element on a sibling element, or via an absolutely positioned `<span>` inside a wrapper `<div>`.

**FR-013** — While the invalid state is active, an ARIA attribute `aria-invalid="true"` must be set on the email input element so that screen readers announce the invalid state.

**FR-014** — A visually hidden or `aria-live` error hint element (e.g., `id="email-error"`) must be associated with the email field via `aria-describedby`. Its text content must be updated to "Please enter a valid email address." when the invalid state is active.

### 5.4 Email Field — Valid State

**FR-015** — When the email field value passes the email format check (`element.validity.valid === true`) and the field is non-empty, the red border and red warning icon must be removed immediately.

**FR-016** — When the valid state is active, the field border must change to green (`#2e7d32` or an equivalent accessible green with at least 3:1 contrast against the white field background).

**FR-017** — When the valid state is active, a green checkmark icon must appear visually inside the right edge of the email input field. The icon must be a recognized success symbol (e.g., Unicode `✓` CHECK MARK or `✅` WHITE HEAVY CHECK MARK). Sizing and positioning must mirror the warning icon specified in FR-011.

**FR-018** — When the valid state is active, `aria-invalid` must be set to `"false"` and the `aria-describedby` error hint text must be cleared.

### 5.5 Email Field — Neutral State

**FR-019** — When the email field is empty (zero characters entered), neither the invalid state nor the valid state must be shown. The field must display in its neutral default border color (`#ccc`) regardless of focus or blur.

**FR-020** — The neutral state must be re-entered if the user clears all characters from the email field after previously entering a value.

### 5.6 Password Field Behavior

**FR-021** — The password field must implement focus-state styling as defined in FR-006. No other visual validation states (invalid, valid, icon) are required or permitted for the password field within this story.

---

## 6. Non-Functional Requirements

### 6.1 Performance

**NFR-001** — The visual state transition (neutral to invalid, invalid to valid, or any reverse transition) must complete within 100 milliseconds of the triggering keystroke as perceived by the user on a mid-range device. No animation delay may be introduced that would make feedback feel lagged. A CSS `transition` on `border-color` of no more than `0.15s ease` is permitted for smoothness and does not violate this constraint.

**NFR-002** — The JavaScript validation logic must execute synchronously on the main thread with no asynchronous calls, network requests, or timers. All computation must complete within a single event-handler invocation.

### 6.2 Accessibility

**NFR-003** — Color must not be the sole indicator of validation state. Each state must also convey meaning through a distinct icon (FR-011 for invalid, FR-017 for valid) so that users who cannot distinguish red from green receive equivalent information.

**NFR-004** — The email field must expose `aria-invalid` and `aria-describedby` attributes as specified in FR-013 and FR-014 so that screen readers (e.g., NVDA, JAWS, VoiceOver) can announce validation state changes.

**NFR-005** — All interactive elements must remain keyboard-navigable. Focus indicators (FR-005, FR-006) must be visible for keyboard-only users and must not be suppressed by `outline: none` without a replacement visible focus style.

**NFR-006** — The warning icon and checkmark icon must have a text alternative accessible to screen readers. If implemented as a `<span>`, it must carry `aria-hidden="true"` since the textual description is provided via `aria-describedby` (FR-014). The icons must not be the only source of information for AT users.

**NFR-007** — The minimum color contrast ratio for validation border colors against the white field background must meet WCAG 2.1 Level AA SC 1.4.11 (Non-text Contrast), requiring at least 3:1.

### 6.3 Browser Compatibility

**NFR-008** — The feature must function correctly in the two most recent stable releases of the following browsers at the time of delivery: Google Chrome, Mozilla Firefox, Apple Safari, and Microsoft Edge. This includes correct rendering of CSS focus styles, JavaScript `validity.valid` API behavior, and icon rendering.

**NFR-009** — The HTML5 Constraint Validation API (`input.validity`) must be used for email format detection. No polyfill is required; browsers that do not support it will fall back to no inline validation, which is acceptable for this story.

### 6.4 Maintainability and Dependencies

**NFR-010** — No external JavaScript libraries (e.g., jQuery, Parsley.js) or external CSS frameworks (e.g., Bootstrap) may be introduced. All new code must be self-contained within `login.html`.

**NFR-011** — The total number of new lines added to `login.html` (CSS and JavaScript combined) must not exceed 80 lines. This keeps the template readable and avoids scope creep.

### 6.5 Graceful Degradation

**NFR-012** — If JavaScript is disabled in the browser, the form must still be submittable. The browser's native HTML5 `type="email"` validation will activate on submit as a fallback. The visual enhancements defined in this story will simply be absent; this is acceptable.

---

## 7. Data and Integration Requirements

### 7.1 Form Data Contract

**DIR-001** — The POST payload from `login.html` to the `/login` route must continue to contain a field named `username`. The email input must use `name="username"` to satisfy this contract (see FR-002).

**DIR-002** — The backend route handler in `app.py` (`request.form.get("username", "").strip()`) must not be modified as part of this story. The only permitted change to `app.py` is updating the USERS dict key from `"admin"` to `"admin@example.com"` (FR-004).

### 7.2 Demo Credential

**DIR-003** — After the change described in FR-004, the working demo credential for local testing is:

- Email: `admin@example.com`
- Password: `password123`

This credential must be documented in the project README or equivalent developer notes so that all team members are aware of the updated login value.

### 7.3 No External Integrations

**DIR-004** — This feature has no integrations with external services, APIs, databases, or authentication providers. It is entirely a frontend enhancement to an existing HTML template.

---

## 8. Acceptance Criteria

The following acceptance criteria are drawn directly from the user story, mapped to requirement IDs for traceability.

---

**AC-1 — Focus State (Both Fields)**

Given I click or tap inside an input field (Email or Password),  
When the field is active (focused),  
Then the field's border must change to a distinct blue color to clearly show it is selected.

Verified by: FR-005, FR-006, FR-008, NFR-005, NFR-007

Verification method: Manual — tab into each field and visually confirm the blue border appears. Automated — CSS computed style check on `:focus` pseudo-class. Keyboard-only navigation test to confirm focus ring is visible.

---

**AC-2 — Invalid Email State**

Given I am typing my email address,  
When I enter an invalid email format (e.g., missing "@" or domain),  
Then the field border must turn red, and a small red warning icon must appear inside the right edge of the field.

Verified by: FR-009, FR-010, FR-011, FR-012, FR-013, FR-014, NFR-001, NFR-003, NFR-004

Verification method: Manual — type `notanemail` into the email field and confirm red border and warning icon appear without pressing submit. Screen reader test — confirm `aria-invalid="true"` and error description are announced. Performance test — confirm state change is visible within 100 ms of keystroke.

---

**AC-3 — Valid Email State**

Given I correct my email to a valid format,  
When the system validates it,  
Then the red border and warning icon must disappear, and a green checkmark must appear to confirm it is valid.

Verified by: FR-015, FR-016, FR-017, FR-018, NFR-001, NFR-003, NFR-004

Verification method: Manual — after triggering AC-2, continue typing to complete a valid email (e.g., `admin@example.com`) and confirm red indicators disappear and green checkmark appears. Screen reader test — confirm `aria-invalid="false"` is updated and error description is cleared.

---

**AC-4 — Neutral State on Empty Field (Derived)**

Given the email field is empty,  
When the page loads or the user clears all text,  
Then neither a red border nor a green border should be shown.

Verified by: FR-019, FR-020

Verification method: Manual — clear the email field after entering text and confirm border returns to neutral gray.

---

**AC-5 — Backend Compatibility (Derived)**

Given the form is submitted with a valid email and correct password,  
When the server processes the login,  
Then authentication must succeed using the updated demo credential `admin@example.com` / `password123`.

Verified by: FR-004, DIR-001, DIR-002, DIR-003

Verification method: Manual end-to-end test — fill in `admin@example.com` and `password123`, submit, confirm redirect to `/dashboard`.

---

## 9. Open Questions and Risks

| ID   | Item | Owner | Status |
|------|------|-------|--------|
| OQ-01 | Should the green checkmark state also trigger on `blur` for users who paste a valid email in one action rather than typing? The current assumption (A-03) covers blur, but explicit confirmation is needed. | Product Owner | Open |
| OQ-02 | Is `#1877f2` (the existing button blue) acceptable for focus borders, or does the design require a lighter/different shade for field focus vs. button color? | Designer | Open |
| OQ-03 | Should the validation suppress the HTML5 native browser validation popup (the browser tooltip on submit) in favour of the inline icon approach, or should both coexist? Suppressing requires `novalidate` on the `<form>` tag and JS-controlled submission gating. | Product Owner | Open |
| OQ-04 | The `admin@example.com` credential change is a non-breaking update to demo data. If a QA or staging environment has a separately configured USERS source (e.g., environment variable or database), those environments must also be updated. Scope of that update is unconfirmed. | Delivery Lead | Open |
| R-01  | Risk: Using `input.validity.valid` delegates the definition of "valid email" to the browser engine. Different browsers may accept or reject edge-case addresses differently (e.g., `user+tag@sub.domain`). If stricter or more permissive validation is needed, a regex must replace the API call. | Developer | Low |
| R-02  | Risk: Absolutely-positioned icon wrappers may misalign on mobile viewports smaller than the 300 px login box width. Responsive icon sizing must be verified on mobile. | Developer | Medium |

---

## 10. Traceability Notes

The table below maps each user story acceptance criterion to its implementing functional requirements and verifying non-functional requirements.

| Acceptance Criterion | Functional Requirements | Non-Functional Requirements |
|---------------------|------------------------|----------------------------|
| AC-1 (Focus state, both fields) | FR-005, FR-006, FR-007, FR-008 | NFR-005, NFR-007 |
| AC-2 (Invalid email — red border + icon) | FR-009, FR-010, FR-011, FR-012, FR-013, FR-014 | NFR-001, NFR-002, NFR-003, NFR-004 |
| AC-3 (Valid email — green checkmark) | FR-015, FR-016, FR-017, FR-018 | NFR-001, NFR-002, NFR-003, NFR-004 |
| AC-4 (Neutral on empty — derived) | FR-019, FR-020 | NFR-001 |
| AC-5 (Backend compatibility — derived) | FR-001, FR-002, FR-003, FR-004 | NFR-012 |

### Requirement Coverage Summary

| Requirement | Traced To |
|-------------|-----------|
| FR-001 | AC-5, Story context |
| FR-002 | AC-5, DIR-001 |
| FR-003 | Story context |
| FR-004 | AC-5, DIR-002, DIR-003 |
| FR-005 | AC-1 |
| FR-006 | AC-1 |
| FR-007 | AC-1 |
| FR-008 | AC-1 |
| FR-009 | AC-2 |
| FR-010 | AC-2 |
| FR-011 | AC-2 |
| FR-012 | AC-2 |
| FR-013 | AC-2 |
| FR-014 | AC-2 |
| FR-015 | AC-3 |
| FR-016 | AC-3 |
| FR-017 | AC-3 |
| FR-018 | AC-3 |
| FR-019 | AC-4 |
| FR-020 | AC-4 |
| FR-021 | AC-1 (password field) |
| NFR-001 — NFR-012 | AC-1 through AC-5 as mapped above |
| DIR-001 — DIR-004 | AC-5 and integration context |

---

*End of Requirements Specification*
