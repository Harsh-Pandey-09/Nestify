# Nestify — Backend

Nestify is an AI-powered rent and flatmate finder platform built using FastAPI, MySQL, WebSockets, and LLM-powered compatibility scoring. The backend provides secure authentication, property management, compatibility scoring, real-time chat, and notification services.

---

## 1. Tech Stack

| Layer          | Technology                                   |
|----------------|-----------------------------------------------|
| API framework  | FastAPI (Python 3.11+)                        |
| Database       | MySQL 8 (via SQLAlchemy ORM + PyMySQL driver)  |
| Auth           | JWT (python-jose) + bcrypt password hashing    |
| Real-time chat | WebSockets (native FastAPI/Starlette)          |
| LLM            | Anthropic Claude (Messages API)                |
| Email          | fastapi-mail (SMTP, any free-tier provider)    |

---

## 2. Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app, router registration, CORS, static files
│   ├── core/
│   │   ├── config.py           # Pydantic settings (.env)
│   │   ├── security.py         # JWT + bcrypt
│   │   └── database.py         # SQLAlchemy engine/session
│   ├── models/                 # SQLAlchemy ORM models (DB schema)
│   ├── schemas/                # Pydantic request/response DTOs
│   ├── routes/                 # API route handlers (one file per resource)
│   ├── services/                # Business logic (LLM, fallback, email, chat, auth...)
│   ├── utils/                  # Small helpers/validators/constants
│   ├── websocket/manager.py    # In-memory WebSocket connection manager
│   ├── uploads/room_images/    # Uploaded listing photos (served as static files)
│   └── dependencies.py         # get_current_user / role guards
├── requirements.txt
├── .env.example
├── run.py
└── README.md
```

---

## 3. Setup Guide

### 3.1 Prerequisites
- Python 3.11+
- MySQL 8.x running locally or a hosted instance (PlanetScale, Railway, RDS, etc.)
- An Anthropic API key (optional — the app works without one via the rule-based fallback)
- SMTP credentials for email (Gmail App Password, Brevo, Mailtrap, etc. — all free tier)

### 3.2 Steps

```bash
# 1. Clone / unzip the project
cd backend

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env: set DATABASE_URL, JWT_SECRET_KEY, ANTHROPIC_API_KEY, MAIL_* vars

# 5. Log into MySQL:
    `mysql -u root -p -e "CREATE DATABASE nestify CHARACTER SET utf8mb4;"`

# 6. Run the app (tables are auto-created on first startup via SQLAlchemy)
python run.py
# or: uvicorn app.main:app --reload

# App runs at http://localhost:8000
# Interactive API docs (Swagger UI): http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

> For production, replace `Base.metadata.create_all()` in `app/main.py` with
> proper Alembic migrations (`alembic init`, then generate/apply revisions).

### 3.3 Environment Variables (`.env.example`)

```env
# --- Database ---
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/nestify

# --- JWT Auth ---
JWT_SECRET_KEY=change_this_to_a_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# --- LLM (Anthropic Claude) ---
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=claude-sonnet-4-6
LLM_TIMEOUT_SECONDS=15

# --- Email (any free SMTP provider) ---
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=your_email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=Nestify

# --- Compatibility threshold that triggers "high match" email to owner ---
HIGH_MATCH_THRESHOLD=80

# --- App ---
FRONTEND_URL=http://localhost:3000
UPLOAD_DIR=app/uploads/room_images
ENV=development
```

### 3.4 Deployment
Works on Render, Railway, or any host supporting Python + MySQL:
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Provision a managed MySQL add-on and set `DATABASE_URL` accordingly.
- Set all `.env` variables in the host's environment/secrets panel.

---

## 4. Database Schema

| Table                 | Key Columns                                                                                   |
|------------------------|-----------------------------------------------------------------------------------------------|
| `users`                | id, name, email (unique), password_hash, role (`tenant`/`owner`/`admin`), is_active           |
| `tenant_profiles`      | id, user_id (FK, unique), preferred_location, budget_min, budget_max, move_in_date, notes     |
| `listings`             | id, owner_id (FK), title, location, rent, available_from, room_type, furnishing_status, photos (CSV), status (`active`/`filled`) |
| `compatibility_scores` | id, tenant_id (FK), listing_id (FK), score (0-100), explanation, source (`llm`/`fallback`), unique(tenant_id, listing_id) |
| `interests`            | id, tenant_id (FK), listing_id (FK), status (`pending`/`accepted`/`declined`), unique(tenant_id, listing_id) |
| `chat_messages`        | id, interest_id (FK), sender_id (FK), message, is_read, created_at (indexed)                  |
| `notifications`        | id, user_id (FK), type, message, is_read, email_sent, created_at                              |

**Relationships**
- `users` 1—1 `tenant_profiles`
- `users` (owner) 1—N `listings`
- `listings` N—N `users` (tenants) via `interests` and `compatibility_scores`
- `interests` 1—N `chat_messages` (chat only unlocks once `interests.status = accepted`)

The compatibility score is **stored once per (tenant, listing) pair** and reused on
subsequent page loads — it's only recomputed when the tenant explicitly calls
`POST /api/compatibility/{listing_id}/recompute` (e.g. after editing their profile).

---

## 5. LLM Integration & Prompt

**Service:** `app/services/llm_service.py` calls the Anthropic Messages API.
**Prompt template:**

```
You are a compatibility scoring engine for a room rental platform.

Given this room listing:
{listing_json}

And this tenant profile:
{tenant_json}

Compute a compatibility score from 0 to 100 based on budget match and location match
(consider partial location matches, e.g. same city/area, as moderately compatible).
Weigh budget fit and location fit roughly equally unless one is a hard mismatch.

Return ONLY valid JSON in this exact shape, with no markdown fences and no extra text:
{"score": <number 0-100>, "explanation": "<one or two sentence explanation>"}
```

### Example Input
```json
// listing
{"title": "Cozy Room in Koramangala", "location": "Koramangala, Bangalore", "rent": 15000,
 "available_from": "2026-08-01", "room_type": "private_room", "furnishing_status": "furnished"}

// tenant profile
{"preferred_location": "Koramangala, Bangalore", "budget_min": 12000, "budget_max": 18000,
 "move_in_date": "2026-08-15"}
```

### Example Output
```json
{"score": 96, "explanation": "The rent of ₹15,000 comfortably fits within the tenant's ₹12,000–18,000 budget, and the listing is in the tenant's exact preferred neighborhood."}
```

### Fallback Handling
If the LLM call throws (timeout, missing API key, malformed JSON, rate limit, etc.),
`compatibility_service.get_or_compute_compatibility()` catches the exception and calls
`fallback_service.compute_fallback_score()` instead — a deterministic rule-based scorer:
- **Budget (0–50 pts):** full marks if rent is inside `[budget_min, budget_max]`; otherwise
  points decay proportionally to how far outside the range the rent falls.
- **Location (0–50 pts):** exact match = 50, substring/partial match = 35, shared keyword
  (e.g. same city) = 30, no match = 5, unknown data = 25 (neutral).

The resulting `Compatibility` row always records which `source` (`llm` or `fallback`)
produced the score, so the fallback is transparent to the frontend/admin.

---

## 6. Real-Time Chat

- Chat is only unlocked once an `Interest` has `status = accepted`.
- Connect: `ws://<host>/ws/chat/{interest_id}?token=<JWT access token>`
- Client → server: `{"type": "message", "message": "text"}` or `{"type": "typing"}`
- Server → client: `{"type": "connected" | "message" | "typing", "data": {...}}`
- Every message is persisted to `chat_messages` **before** being broadcast, so chat
  history (`GET /api/chat/{interest_id}/messages`) is always consistent even if a
  client reconnects or was offline.
- `app/websocket/manager.py` keeps an in-memory map of `interest_id → set(sockets)`
  (a "room" per accepted interest) and removes dead sockets on send failure.

---

## 7. Notification Flow

| Event                                   | Recipient | Type                    | Email? |
|------------------------------------------|-----------|--------------------------|--------|
| Tenant expresses interest, score ≥ 80    | Owner     | `high_match_interest`    | Yes    |
| Tenant expresses interest, score < 80    | Owner     | `interest_received`      | Yes    |
| Owner accepts interest                   | Tenant    | `interest_accepted`      | Yes    |
| Owner declines interest                  | Tenant    | `interest_declined`      | Yes    |
| Owner marks listing filled               | Owner     | `listing_filled`         | No (in-app only) |
| New chat message                         | Other participant | `new_message`    | No (in-app only, avoids email spam) |

Every notification is written to the `notifications` table first (source of truth,
always succeeds), then an email is attempted via `email_service.send_email()`. Email
failures are caught and logged — `notification.email_sent` is simply `False` — so a
broken SMTP config never breaks the underlying API request.

---

## 8. API Reference

Base URL: `http://localhost:8000`. All protected routes require
`Authorization: Bearer <token>`.

### Auth (`/api/auth`)
| Method | Path              | Auth | Body / Notes                                   |
|--------|-------------------|------|-------------------------------------------------|
| POST   | `/register`       | none | `{name, email, password, role: tenant\|owner}` → `TokenResponse` |
| POST   | `/login`          | none | `{email, password}` → `TokenResponse`           |
| GET    | `/me`              | any  | → `UserResponse`                                |

### Users (`/api/users`)
| Method | Path     | Auth | Notes                              |
|--------|----------|------|--------------------------------------|
| GET    | `/me`    | any  | → `UserResponse`                     |
| PUT    | `/me`    | any  | `{name?, password?}` → `UserResponse`|

### Tenant Profile (`/api/tenant`)
| Method | Path        | Auth   | Notes |
|--------|-------------|--------|-------|
| POST   | `/profile`  | tenant | `TenantProfileCreateRequest` → `TenantProfileResponse` |
| GET    | `/profile`  | tenant | → `TenantProfileResponse` |
| PUT    | `/profile`  | tenant | `TenantProfileUpdateRequest` (partial) → `TenantProfileResponse` |

### Listings (`/api/listings`)
| Method | Path                        | Auth   | Notes |
|--------|-----------------------------|--------|-------|
| POST   | `` (root)                   | owner  | `ListingCreateRequest` → `ListingResponse` |
| GET    | `/owner/mine`                | owner  | → `List[ListingResponse]` |
| GET    | `/{listing_id}`              | any    | → `ListingResponse` |
| PUT    | `/{listing_id}`              | owner  | `ListingUpdateRequest` (partial, owner-only) |
| DELETE | `/{listing_id}`              | owner  | owner-only |
| PATCH  | `/{listing_id}/fill`         | owner  | marks filled, hides from search, notifies owner |
| POST   | `/{listing_id}/photos`       | owner  | multipart `files[]` upload → `ListingResponse` |
| GET    | `` (root, query params)      | tenant/any | filters + AI-ranked results, see below |

**Browse/search query params:** `location`, `min_budget`, `max_budget`, `room_type`,
`furnishing_status`, `sort_by` (`compatibility` default, or `rent_asc`/`rent_desc`/`newest`),
`page`, `page_size` → `PaginatedListingsResponse` (each result includes
`compatibility_score`, `compatibility_explanation`, `compatibility_source`).

### Compatibility (`/api/compatibility`)
| Method | Path                          | Auth   | Notes |
|--------|-------------------------------|--------|-------|
| GET    | `/{listing_id}`                | tenant | cached score (computes+caches if missing) → `CompatibilityResponse` |
| POST   | `/{listing_id}/recompute`      | tenant | forces a fresh LLM/fallback computation |

### Interest (`/api/interest`)
| Method | Path                     | Auth   | Notes |
|--------|--------------------------|--------|-------|
| POST   | `` (root)                | tenant | `{listing_id}` → creates interest, notifies owner (email if score ≥ threshold) |
| GET    | `/sent`                   | tenant | interests the tenant has sent |
| GET    | `/received`               | owner  | interests received on the owner's listings |
| PATCH  | `/{interest_id}/accept`   | owner  | unlocks chat, notifies tenant |
| PATCH  | `/{interest_id}/decline`  | owner  | notifies tenant |

### Chat
| Method | Path                                | Auth | Notes |
|--------|--------------------------------------|------|-------|
| GET    | `/api/chat/{interest_id}/messages`  | any participant | → `ChatHistoryResponse` (403 unless interest accepted) |
| WS     | `/ws/chat/{interest_id}?token=...`  | any participant | real-time messaging, see §6 |

### Notifications (`/api/notifications`)
| Method | Path                          | Auth | Notes |
|--------|--------------------------------|------|-------|
| GET    | `` (root)                     | any  | → `List[NotificationResponse]` |
| PATCH  | `/{notification_id}/read`     | any  | `{is_read: bool}` |

### Admin (`/api/admin`)
| Method | Path                     | Auth  | Notes |
|--------|--------------------------|-------|-------|
| GET    | `/users`                  | admin | list all users |
| DELETE | `/users/{user_id}`       | admin | deactivate (soft delete) |
| GET    | `/listings`               | admin | list all listings (any status) |
| DELETE | `/listings/{listing_id}` | admin | hard delete |
| GET    | `/activity`               | admin | → `AdminActivitySummary` (counts across users/listings/interests/messages/scores) |

Full interactive schema (all DTOs, enums, example payloads) is auto-generated at
`/docs` (Swagger) and `/redoc` once the server is running.

---

## 9. DTOs (Pydantic Schemas) Quick Reference

All request/response bodies live in `app/schemas/`. Key ones for frontend integration:

- `UserRegisterRequest`, `UserLoginRequest`, `TokenResponse`, `UserResponse`
- `TenantProfileCreateRequest/UpdateRequest/Response`
- `ListingCreateRequest/UpdateRequest`, `ListingResponse`, `ListingWithScoreResponse`, `PaginatedListingsResponse`
- `CompatibilityResponse`, `LLMCompatibilityResult`
- `InterestCreateRequest`, `InterestStatusUpdateRequest`, `InterestResponse`
- `ChatMessageCreateRequest/Response`, `ChatHistoryResponse`, `WSIncomingMessage`, `WSOutgoingMessage`
- `NotificationResponse`, `NotificationMarkReadRequest`
- `AdminActivitySummary`, `MessageResponse`, `ErrorResponse`

Enums: `UserRole` (tenant/owner/admin), `RoomType` (private_room/shared_room/entire_place),
`FurnishingStatus` (furnished/semi_furnished/unfurnished), `ListingStatus` (active/filled),
`InterestStatus` (pending/accepted/declined), `NotificationType` (high_match_interest,
interest_received, interest_accepted, interest_declined, new_message, listing_filled).

---

## 10. Testing

A quick smoke test (register → listing → profile → compatibility → interest → accept →
chat → notifications → fill) was run against an in-memory SQLite DB using
`fastapi.testclient.TestClient` to validate the full flow end-to-end, including the
WebSocket chat channel. Swap `DATABASE_URL` to your MySQL instance for real use.
