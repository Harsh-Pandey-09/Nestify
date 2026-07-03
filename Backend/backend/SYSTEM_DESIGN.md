# System Design Write-Up — Nestify

## 1. Compatibility Scoring Design

Compatibility is modeled as a first-class entity, not a derived/on-the-fly number: the
`compatibility_scores` table stores one row per `(tenant_id, listing_id)` pair with a
`score` (0–100), an `explanation`, a `source` flag (`llm` or `fallback`), and timestamps.
This is deliberate — LLM calls are slow and cost money, so recomputing on every browse
request would be wasteful since preferences and listing attributes rarely change between
page loads.

The read path (`GET /api/listings`, `GET /api/compatibility/{id}`) always checks the
cache first via `compatibility_service.get_or_compute_compatibility()`. On a cache miss
(new tenant/listing combination) it computes and persists the score inline, so the very
first view is slightly slower but every subsequent view is a simple indexed lookup. A
`UNIQUE(tenant_id, listing_id)` constraint prevents duplicate rows, and a separate
`POST /api/compatibility/{id}/recompute` endpoint lets the frontend force a refresh —
intended to be called after a tenant edits their profile (budget/location change), since
that invalidates any previously cached scores for that tenant.

When a tenant browses listings, results can be sorted by cached score (`sort_by=compatibility`,
the default) alongside conventional filters (location substring match, rent range, room
type, furnishing). Because scores are cached per pair, ranking N listings for a tenant is
O(N) lookups against an indexed table rather than N LLM calls — this is what keeps the
"ranked listings" browse endpoint fast even as the catalog grows.

## 2. LLM Integration and Fallback

`llm_service.py` isolates all Anthropic API interaction behind a single function,
`get_llm_compatibility_score()`, which builds a fixed prompt template (listing JSON +
tenant JSON, instructed to return bare JSON with `score` and `explanation`), calls the
Messages API, strips any accidental markdown fences, parses the JSON, and clamps the
score to [0, 100] as a defensive measure against a misbehaving model.

Reliability is handled one layer up, in `compatibility_service.py`: the LLM call is
wrapped in a broad `try/except`. Any failure mode — missing API key, network timeout,
rate limiting, or a response that isn't valid JSON — is caught and logged, and control
falls through to `fallback_service.compute_fallback_score()`, a deterministic rule-based
scorer that never fails. It splits the 100 points into two 50-point buckets: budget fit
(full marks inside the tenant's range, decaying proportionally to how far rent falls
outside it) and location fit (exact, partial, shared-keyword, or no match). This keeps
the platform's core matching feature working even if the LLM is down, misconfigured, or
the API key is absent — which matters since scoring gates ranked browse and the
"high match" owner notification. The `source` field on every stored score makes the
fallback fully auditable rather than silently degrading quality.

## 3. Real-Time Chat Implementation

Chat is scoped to an `Interest` record and only unlocked once its status is `accepted` —
this is enforced both on the REST history endpoint and on WebSocket connect, so a
declined or still-pending interest cannot be used to message a stranger. The WebSocket
route (`/ws/chat/{interest_id}?token=...`) authenticates via the same JWT used for REST
calls (passed as a query param, since browser WebSocket clients can't set custom headers),
then verifies the connecting user is either the tenant or the listing's owner for that
specific interest before accepting the connection.

`app/websocket/manager.py` is a lightweight in-memory `ConnectionManager` that maps each
`interest_id` to the set of currently-connected sockets (effectively a "room"). Every
incoming message is persisted to the `chat_messages` table via `chat_service.persist_message()`
*before* being broadcast — so message history is durable and consistent even if a
participant is offline, reconnects, or the connection drops mid-conversation; `GET
/api/chat/{interest_id}/messages` always reflects the source of truth in MySQL, not
just what's currently in memory. Dead sockets are pruned automatically on a failed send.
This in-memory approach is simple and sufficient for a single-server deployment; scaling
to multiple app instances would require swapping the manager for a Redis pub/sub backend
so broadcasts reach sockets connected to other processes.

## 4. Notification Flow

Every notable event — a tenant expressing interest, an owner accepting/declining, or a
listing being marked filled — first writes a row to the `notifications` table (the
in-app source of truth, which always succeeds as a local DB write), then attempts a
corresponding email via `email_service.send_email()` using `fastapi-mail` over SMTP. The
send is wrapped so failures (bad credentials, provider downtime) are caught, logged, and
reflected as `email_sent = False` — never breaking the underlying request (e.g. accepting
an interest still succeeds even if the confirmation email fails).

Interest-expressed notifications branch on the tenant's compatibility score for that
listing: scores at or above `HIGH_MATCH_THRESHOLD` (default 80) are tagged
`high_match_interest` to signal urgency to the owner, while lower scores use the plainer
`interest_received` type — both are emailed, but a frontend could visually prioritize the
former. Chat messages also generate in-app notifications for the offline participant, but
deliberately skip email to avoid spamming users during an active conversation.
