# LIVING PROJECT MAP: {{PROJECT_NAME}} v1.0
> **Purpose:** Agent's primary working memory and architectural compass. Read this file BEFORE scanning code.
> **Last Updated:** {{UPDATED_AT}} | Commit: {{COMMIT_HASH}}
>
> **AGENT PROTOCOL:**
> 1. Read MODULE 5 (Feature Cross-Reference) to identify components related to current task.
> 2. Read MODULE 3 (UI & DOM Map) to trace user interface triggers to client logic.
> 3. Check MODULE 1 & 2 (Code Location Index) for exact `file:line` surgery targets.
> 4. Verify MODULE 4 (Implicit Constraints) BEFORE making any code edits.
> 5. Run tests, then update this map using `living_map.py update`.

---

## MODULE 0: META & ENVIRONMENT

| Attribute | Specification |
|---|---|
| Tech Stack | {{STACK}} |
| Entry Point | `{{ENTRY_POINT}}` |
| Primary Database | `{{DATABASE}}` |
| Test Framework | `{{TEST_FRAMEWORK}}` |
| Active Tests Count | {{TEST_COUNT}} tests |
| Current Branch | `main` |

---

## MODULE 1: CODE LOCATION INDEX — Backend & Core Services
> Used for surgical, targeted modifications. Format: `file:line → symbol()`

### {{BACKEND_SAMPLE_FILE}}

| Line | Symbol | Description |
|------|--------|-------------|
| L10 | `InitServer()` | Server bootstrap and dependency injection |
| L45 | `AuthMiddleware()` | JWT token authentication guard |
| L80 | `HandleGetItems()` | Fetches paginated items |

---

## MODULE 2: CODE LOCATION INDEX — Frontend & Client Logic
> Format: `file:line → function()`

### {{FRONTEND_SAMPLE_FILE}}

| Line | Symbol | Description |
|------|--------|-------------|
| L15 | `initApp()` | DOM ready event listeners & state hydration |
| L60 | `renderItems()` | Renders item cards into DOM container |
| L120 | `onFormSubmit()` | Serializes input, calls API, shows toast |

---

## MODULE 3: UI & DOM ELEMENT MAP
> Mapping physical UI elements to logic and backend endpoints.

| UI Selector / Element ID | Event / Trigger | Client Function | Target API Endpoint | Notes |
|---|---|---|---|---|
| `#btn-submit-order` | `click` | `submitOrder()` | `POST /api/orders` | Disable during request |
| `#filter-status-select`| `change`| `filterOrders()` | `GET /api/orders?status=` | Preserves pagination |
| `.modal-user-edit` | `show.bs.modal` | `populateUser()` | `GET /api/users/:id` | Autofocus first input |

---

## MODULE 4: IMPLICIT CONSTRAINTS & ANTI-PATTERNS
> **CRITICAL:** Rules and domain traps learned the hard way that static code analysis CANNOT deduce.

- [C1] **State vs DOM Hierarchy:** Do not rely solely on cached memory state when user inputs have changed; read active DOM values directly.
- [C2] **Database Locking / WAL Mode:** On embedded databases (e.g. SQLite), keep transactions short and avoid long-running writes in HTTP handlers.
- [C3] **Mobile Responsive Invariants:** Fixed bottom bars must preserve dynamic viewport safe-area padding (`env(safe-area-inset-bottom)`).
- [C4] **Snapshot & Background Sync:** Background snapshots are asynchronous; never assume immediate consistency after dispatching async workers.

---

## MODULE 5: FEATURE CROSS-REFERENCE MATRIX
> Cross-layer end-to-end trace: From user click to database write.

| Feature ID | Description | UI Selector / DOM | Frontend JS | Backend API | Database Model / Table | Constraints |
|---|---|---|---|---|---|---|
| F001 | User Authentication | `#form-login` | `login()` in `auth.js` | `POST /api/login` | `users` | C1 |
| F002 | Item Listing | `#item-grid` | `loadItems()` in `app.js` | `GET /api/items` | `items` | C2 |

---

## MODULE 6: TESTING & QUALITY GATE

| Metric / Check | Value |
|---|---|
| Test Directory | `{{TEST_DIR}}` |
| Primary Test Command | `{{TEST_COMMAND}}` |
| Regression Scope | All tests must PASS 100% before commit |
| Test Data Teardown | Zero-pollution policy: Clean all mock records after run |

---

## MODULE 7: PRE-EDIT CHECKLIST & GUARDRAILS
- [ ] Read relevant sections in this MAP before touching code.
- [ ] Check MODULE 4 constraints against proposed changes.
- [ ] Run impact analysis on symbol callers and callees.
- [ ] Write/update automated tests covering happy path and edge cases.
- [ ] Run `python scripts/living_map.py update` to sync line numbers.
- [ ] Perform Atomic Git Commit (code + map together).

---

## MODULE 8: RECENT EXECUTION HISTORY
- `{{COMMIT_HASH}}` — Initialized Living Project Map.
