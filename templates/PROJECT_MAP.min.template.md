# LIVING PROJECT MAP (COMPACT AI WORKING MEMORY)
> **Notice:** This is the token-efficient compact map. Read this first (~300-500 tokens).
> For exact line surgery, query the full map or use: `python living_map.py impact <symbol>`

## MODULE 0: META
| Attribute | Value |
|---|---|
| Tech Stack | {{STACK}} |
| Entry Point | `{{ENTRY_POINT}}` |
| Primary Database | `{{DATABASE}}` |
| Test Framework | `{{TEST_FRAMEWORK}}` |
| Codebase-MD5 | `{{CODEBASE_MD5}}` |

---

## MODULE 1 & 2: EXPORTED SYMBOLS SUMMARY
- **backend_core:** `InitServer`, `AuthMiddleware`, `HandleGetItems`
- **frontend_app:** `initApp`, `renderItems`, `onFormSubmit`

---

## MODULE 3: UI & DOM ELEMENT MAP
| UI Selector | Event | Client Function | Target API Endpoint |
|---|---|---|---|
| `#btn-submit-order` | `click` | `submitOrder()` | `POST /api/orders` |
| `#filter-status-select` | `change` | `filterOrders()` | `GET /api/orders?status=` |

---

## MODULE 4: IMPLICIT CONSTRAINTS & ANTI-PATTERNS
- [C1] **State vs DOM Hierarchy:** Always read active DOM values if user inputs change without blur.
- [C2] **Database Locking / WAL Mode:** Keep write transactions short in HTTP handlers.
- [C3] **Mobile Responsive Invariants:** Preserve safe-area-inset padding for fixed navigation bars.

---

## MODULE 5: FEATURE CROSS-REFERENCE MATRIX
| Feature ID | Description | UI Selector | Frontend JS | Backend API | Database Model | Constraints |
|---|---|---|---|---|---|---|
| F001 | User Authentication | `#form-login` | `login()` | `POST /api/login` | `users` | C1 |
| F002 | Item Listing | `#item-grid` | `loadItems()` | `GET /api/items` | `items` | C2 |
