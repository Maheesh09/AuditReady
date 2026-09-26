# API contract

> Written in full on **Day 2 (BE-03), before endpoint code.** Source of truth for backend and frontend.
> Endpoint list: Development Plan Section 8.

## Conventions

- Base path: `/api/v1`
- Auth: `Authorization: Bearer <Supabase JWT>` on every endpoint except `/health`.
- The factory is always resolved from the authenticated user, **never from the request body or URL**.
- IDs from the URL that belong to another factory return `404` (not `403`) so existence is not revealed.
- OpenAPI: `GET /api/v1/openapi.json`. Frontend types are generated with `npm run gen:api`.

## Error format (all endpoints)

```json
{ "error_code": "UNSUPPORTED_FILE_TYPE", "message": "Only PDF, PNG, JPG, XLSX and CSV files are accepted." }
```

Codes: `UNSUPPORTED_FILE_TYPE`, `FILE_TOO_LARGE`, `TOO_MANY_PAGES`, `OCR_FAILED`, `NOT_FOUND`,
`FORBIDDEN`, `RATE_LIMITED`, `LLM_UNAVAILABLE`, `VALIDATION_ERROR`.

## Endpoints

### `GET /health` (implemented)

No auth. Liveness check.

```json
200 { "status": "ok" }
```

<!-- Day 2: add request/response examples for every endpoint in Plan Section 8. -->
