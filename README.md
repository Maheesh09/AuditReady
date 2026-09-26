# AuditReady

Turns a Sri Lankan apparel factory's messy compliance documents into a buyer-ready, verified
questionnaire, with every answer linked to its source. **The system never invents compliance
evidence: "No evidence found" is always better than a wrong answer.**

IntelliCon '26 AI Buildathon. The single source of truth for the build is the Development Plan.

## Repository layout

| Path | What lives there |
|---|---|
| `backend/` | FastAPI API, processing pipeline, validation rules, AI answer generation |
| `frontend/` | React + TypeScript + Tailwind + shadcn/ui app |
| `data/` | Synthetic demo documents, ground truth, questionnaire, golden eval set |
| `eval/` | Extraction and answer eval scripts; dated results are committed |
| `scripts/` | Synthetic doc generation, demo seeding, temp bucket sweep |
| `docs/` | API contract, decision log, demo script |

## Prerequisites

- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- Node.js 22+

## Run locally

```bash
# Backend  → http://localhost:8000/docs
cd backend
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload

# Frontend → http://localhost:5173
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

## Checks (the same ones CI runs)

```bash
# backend
uv run ruff format --check . && uv run ruff check . && uv run mypy && uv run pytest && uv run pip-audit --skip-editable

# frontend
npm run lint && npm run format:check && npm run typecheck && npm test && npm run build
```

## Working rules (Development Plan Section 4)

- Trunk-based. Branch from `main` as `type/TASK-ID-short-name` (e.g. `feat/BE-07-upload-endpoint`), merge within a day.
- Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `eval:`, `prompt:`, `docs:`, `chore:`, `db:`.
- PRs under ~400 changed lines, one approval, green CI, squash-merge.
- AI changes get the `ai-change` label, which runs the eval workflow. A drop in any gated metric blocks the merge.
- Never commit secrets. If one leaks: rotate first, then clean history.
