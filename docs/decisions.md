# Decision log

Short log of every technical decision. Newest at the bottom. Format: date, decision, why.

- **2026-09-28** Monorepo `auditready` with `backend/`, `frontend/`, `data/`, `eval/`, `scripts/`, `docs/` (Plan Section 6).
- **2026-09-28** Backend uses `uv` with `package = false`: it is an application, not a library, so no build backend or editable install is needed. Tests import `app` via `pythonpath = ["."]`.
- **2026-09-28** mypy runs in `strict` mode from Day 1. Adding strictness later means fixing hundreds of errors at once.
- **2026-09-28** ESLint + Prettier instead of the `oxlint` the current Vite template ships, to follow Plan Section 4.4.
- **2026-09-28** TypeScript pinned to `~5.9` (the template picked 6.0) because `openapi-typescript` 7 only supports TypeScript 5, and the generated API client is mandatory (Plan 4.4).
- **2026-09-28** Tailwind CSS v4 via `@tailwindcss/vite` (no `tailwind.config.js`; tokens live in `src/index.css` under `@theme`). shadcn/ui is configured through `components.json`; add components with `npx shadcn@latest add <name>`.
- **2026-09-28** CI workflows have **no path filters**. They are required status checks, and a filtered-out required check never reports, which would block PRs that only touch the other half of the repo.
- **2026-09-28** OpenAPI served at `/api/v1/openapi.json` in every environment (the frontend client is generated from it); the Swagger UI at `/docs` is disabled in production.
