# AGENTS.md — News Radar Project Operating Guide for Codex

> This file is the persistent AI working agreement for OpenAI Codex sessions in this repository.
> Every Codex execution MUST read and follow this document before making any changes.
> This file mirrors the conventions in `CLAUDE.md` so both AI agents produce coherent, compatible work.

---

## 1. Project Mission

**News Radar** is a news-monitoring product that:

- Ingests content from websites (RSS/scraping), YouTube channels, X/Twitter accounts, LinkedIn pages, and other pluggable source types.
- Maintains multiple **profiles**, each defining topics of interest, uninteresting topics, keywords, weights/priorities, and relevance signals.
- Classifies every ingested item against each profile's criteria.
- Sends notifications through configurable channels (email, Telegram, Slack, Odoo, and future adapters).

The product is built as a **modular monorepo** with a React admin frontend and a Python backend service.

---

## 2. MVP-First Philosophy

- Ship the smallest useful vertical slice first.
- Every feature must justify its presence in the current iteration.
- Mark anything beyond the current scope as `# FUTURE:` in comments or docs—never implement it speculatively.
- Prefer working software over comprehensive documentation, but keep this file and `CLAUDE.md` current.

---

## 3. Architectural Principles

| Principle | Meaning |
|---|---|
| **Modular monorepo** | Frontend and backend live in one repo with clear boundaries. |
| **Hexagonal-lite** | Use ports/adapters for external integrations (sources, notifications, storage) without over-abstracting internal logic. |
| **Dependency inversion at boundaries** | Core business logic must not import framework or infrastructure code directly. Define interfaces; implement adapters. |
| **Single Responsibility per module** | Each source connector, notification adapter, or classification strategy is one module with one job. |
| **Configuration over code** | Profiles, sources, keywords, and channel settings are data, not hard-coded behavior. |
| **Fail gracefully** | Ingestion failures, rate limits, and duplicates are expected. Log, skip, and continue. Never crash the pipeline. |
| **Extensibility over premature complexity** | Add extension points (registries, plugin patterns) only where variation is already known. Do not abstract hypothetical futures. |

---

## 4. Monorepo Structure

```
news-radar/
├── CLAUDE.md                  # AI operating guide (Claude Code)
├── AGENTS.md                  # AI operating guide (Codex) — this file
├── README.md                  # Human-facing project overview
├── .github/                   # GitHub workflows, PR templates (future)
│
├── frontend/                  # React admin UI
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Route-level page components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API client functions
│   │   ├── types/             # TypeScript type definitions
│   │   └── utils/             # Pure helper functions
│   └── public/
│
├── backend/                   # Python service
│   ├── pyproject.toml         # Project metadata and dependencies
│   ├── alembic/               # Database migrations (when needed)
│   ├── src/
│   │   └── news_radar/
│   │       ├── __init__.py
│   │       ├── main.py            # App entry point
│   │       ├── config.py          # Settings / env loading
│   │       ├── api/               # HTTP route handlers
│   │       ├── core/              # Domain models, interfaces, business logic
│   │       │   ├── models.py
│   │       │   ├── interfaces.py  # Abstract base classes / protocols
│   │       │   └── classification.py
│   │       ├── sources/           # Source connector modules (pluggable)
│   │       │   ├── base.py        # Source interface
│   │       │   ├── rss.py
│   │       │   ├── youtube.py
│   │       │   ├── twitter.py
│   │       │   ├── linkedin.py
│   │       │   └── ...
│   │       ├── notifications/     # Notification adapter modules (pluggable)
│   │       │   ├── base.py        # Notification interface
│   │       │   ├── email.py
│   │       │   ├── telegram.py
│   │       │   ├── slack.py
│   │       │   └── ...
│   │       ├── scheduler/         # Periodic job orchestration
│   │       ├── storage/           # Repository pattern for persistence
│   │       └── utils/
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── conftest.py
│
└── docs/                      # Architecture decisions, API specs (future)
```

> This structure is a target layout. Create directories and files only as needed—do not scaffold empty placeholder files.

---

## 5. Technology Stack

### Frontend
- **React 18+** with TypeScript
- **TailAdmin** (free React + Tailwind CSS template) as the UI foundation
- **Vite** as the build tool
- **Tailwind CSS** for styling
- Do NOT rewrite, vendor, or fork TailAdmin internals. Extend through composition.

### Backend
- **Python 3.11+**
- **FastAPI** as the web framework
- **Pydantic** for data validation and settings
- **SQLAlchemy** (async) for ORM
- **APScheduler** or **Celery** for scheduled ingestion jobs (choose when needed)
- **httpx** for async HTTP client operations
- **pytest** for testing

### General
- Git + GitHub for version control
- Conventional-style commits (see §10)
- Environment variables for secrets and configuration (never commit secrets)

---

## 6. Coding Standards

### Python (backend)
- Follow PEP 8. Use `ruff` for linting and formatting.
- Type-hint all function signatures.
- Use `async`/`await` for I/O-bound operations.
- Keep functions under ~30 lines. Extract when logic is reusable or complex.
- Use `Protocol` or `ABC` for interfaces at boundaries (sources, notifications, storage).
- Name modules and classes clearly: `RSSSourceConnector`, `TelegramNotifier`, `ProfileClassifier`.

### TypeScript (frontend)
- Strict TypeScript (`"strict": true`).
- Functional components with hooks. No class components.
- Colocate component-specific types with the component file.
- Use named exports. Avoid default exports except for page-level components.
- Keep components focused. Extract logic into custom hooks when it grows.

### General
- No commented-out code in committed files.
- No `TODO` without a linked issue or `# FUTURE:` tag.
- Prefer explicit over implicit. Prefer readable over clever.

---

## 7. Testing Strategy

| Layer | Tool | Expectation |
|---|---|---|
| Backend unit tests | pytest | Cover core logic, classification, and utility functions |
| Backend integration tests | pytest + httpx | Cover API endpoints and source/notification adapters with mocks |
| Frontend unit tests | Vitest + Testing Library | Cover hooks, utility functions, and critical component behavior |
| E2E tests | (future) Playwright or Cypress | Deferred until UI is stable |

- Write tests for new logic. Do not add tests retroactively for code you did not change.
- Test behavior, not implementation. Mock external boundaries only.
- Ingestion connectors must have tests using recorded/fixture responses, never live API calls in CI.

---

## 8. Source Connectors — Convention

Every source connector MUST:
1. Implement the `SourceConnector` protocol/interface defined in `backend/src/news_radar/sources/base.py`.
2. Accept configuration (URL, API key, polling interval) via constructor or config object.
3. Return a standardized list of `IngestedItem` domain objects.
4. Handle its own errors internally (log + return empty or partial results on failure).
5. Be registered in a connector registry so the scheduler can discover it.
6. Include unit tests with fixture data.

```python
# Conceptual interface (do not implement yet)
class SourceConnector(Protocol):
    async def fetch_items(self, since: datetime | None = None) -> list[IngestedItem]: ...
    def source_type(self) -> str: ...
```

New source types are added by creating a new module in `sources/` and registering it. No core code changes should be required.

---

## 9. Notification Adapters — Convention

Every notification adapter MUST:
1. Implement the `Notifier` protocol/interface in `backend/src/news_radar/notifications/base.py`.
2. Accept per-profile or per-channel configuration.
3. Send a formatted message for a classified item.
4. Handle delivery failures gracefully (log, retry logic optional).
5. Be registered in an adapter registry.
6. Include unit tests with mocked external calls.

```python
# Conceptual interface (do not implement yet)
class Notifier(Protocol):
    async def send(self, item: ClassifiedItem, profile: Profile) -> bool: ...
    def channel_type(self) -> str: ...
```

New channels are added by creating a new module in `notifications/` and registering it. No core code changes should be required.

---

## 10. Commit Workflow

- **Commits pequeños y atómicos.** Cada commit debe hacer una sola cosa y ser comprensible de forma independiente.
- **Formato del mensaje de commit:** `tipo(ámbito): descripción breve en español`
  - Tipos: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `style`
  - Ámbito: `backend`, `frontend`, `sources`, `notifications`, `core`, `config`, etc.
  - Ejemplo: `feat(sources): añadir conector RSS con tests de fixtures`
- **Los mensajes de commit siempre se escriben en español.**
- Nunca combinar cambios no relacionados en un solo commit.
- Cada ejecución de Codex debe producir uno o más commits representando el trabajo completado.
- No modificar ni aplastar commits existentes salvo que se pida explícitamente.

---

## 11. Codex Behavior Rules

When executing a task in this repository, Codex MUST follow these rules:

### Before starting
1. Read this `AGENTS.md` (and `CLAUDE.md` if additional context is needed) to understand conventions.
2. Understand the current state of the codebase (check existing files, recent commits).
3. Identify which part of the architecture the task touches.

### Scoping the task
4. Break the request into the smallest deliverable unit.
5. If the request is ambiguous, state your interpretation and the assumptions you are making before writing code.
6. If the request exceeds MVP scope, implement only the MVP portion and note the remainder as future work.

### During implementation
7. **Do not overengineer.** Implement what is asked. Do not add features, abstractions, or refactors beyond the request.
8. **Keep changes atomic.** Touch only the files necessary for the task.
9. **Respect existing patterns.** Match the style, naming, and structure already in the codebase.
10. **Do not introduce new dependencies** without stating the reason and confirming they are justified.
11. **Write tests** for new logic. Skip tests only for trivial configuration or boilerplate.
12. **Handle errors at boundaries.** Source connectors catch their own exceptions. Notification adapters handle delivery failures. API endpoints return proper error responses.
13. **Never hard-code secrets, API keys, or environment-specific values.**

### Describing changes
14. After implementation, summarize what was done: files created/modified, key decisions, and any assumptions made.
15. List any deviations from this guide and justify them.

### Protecting architecture
16. Do not move, rename, or restructure existing modules unless the task specifically requires it.
17. Do not change interfaces (`base.py` protocols) without confirming impact on existing implementations.
18. New source connectors go in `sources/`. New notification adapters go in `notifications/`. New API routes go in `api/`. Do not scatter responsibilities.
19. If a task would require breaking an architectural boundary, stop and describe the conflict instead of proceeding.

### Ending every execution
20. **Terminar siempre con exactamente 5 ideas** de mejoras, próximos pasos o funcionalidades relacionadas. **Escritas en español.** Formato:

```
## Próximos pasos — 5 Ideas
1. <idea>
2. <idea>
3. <idea>
4. <idea>
5. <idea>
```

Deben ser relevantes a lo que se acaba de construir o a prioridades adyacentes.

---

## 12. Assumptions Policy

- Make **minimal assumptions**. When something is ambiguous, prefer asking or stating the assumption explicitly over guessing.
- When an assumption must be made to proceed, document it inline with `# ASSUMPTION:` and in the execution summary.
- Never treat an assumption as a confirmed requirement in future sessions.
- If a previous assumption is later contradicted, update the code and remove the assumption marker.

---

## 13. Architectural Coherence Over Time

- This document and `CLAUDE.md` are the sources of truth for project structure and conventions.
- If a future task conflicts with this guide, follow this guide unless the user explicitly overrides it.
- When the user makes a decision that changes architectural direction, update **both** `AGENTS.md` and `CLAUDE.md` as part of that execution.
- Do not allow incremental drift: each change must fit within the defined structure or trigger an explicit update to the structure.

---

## 14. Incremental Feature Delivery

When adding any feature:
1. **Define the interface first** (protocol/type), then implement.
2. **Implement the simplest version** that fulfills the requirement.
3. **Add a test** that verifies the expected behavior.
4. **Register/wire** the new component into the existing system.
5. **Commit** with a descriptive message in Spanish.
6. **Document** any new extension point or pattern introduced.

Do not build multiple features in one execution unless they are tightly coupled and small.

---

## 15. Future Considerations (Do Not Implement Yet)

These are acknowledged directions that should influence design decisions but should NOT be built until explicitly requested:

- **CI/CD pipelines** (GitHub Actions for lint, test, build)
- **Docker / containerization** for local dev and deployment
- **Database migrations** (Alembic) once persistence is added
- **Authentication/authorization** for the admin UI
- **Rate limiting and backoff** strategies for source connectors
- **Deduplication** logic for ingested items across sources
- **Advanced classification** (NLP/ML-based relevance scoring beyond keyword matching)
- **Webhook-based ingestion** (push sources instead of polling)
- **Multi-tenancy** (if the product serves multiple organizations)
- **Internationalization** of the frontend

---

## 16. Codex-Specific Notes

- Codex runs in a sandboxed environment. If you need to install dependencies, use `pip install -e ".[dev]"` in `backend/` or `npm install` in `frontend/`.
- Codex should verify its changes compile and pass tests before presenting results.
- When Codex and Claude Code both contribute to this repo, consistency is paramount. Always check recent commits and existing patterns before writing new code.
- If you are unsure whether a convention exists, check `CLAUDE.md`, this file, and the existing codebase before inventing a new pattern.
- Prefer reading existing test fixtures (`tests/conftest.py`) and reusing them over creating duplicates.

---

## Summary of Key Conventions

| Area | Convention |
|---|---|
| Repo layout | `frontend/` + `backend/` at root |
| Frontend stack | React + TypeScript + Vite + TailAdmin + Tailwind CSS |
| Backend stack | Python 3.11+ + FastAPI + Pydantic + SQLAlchemy (async) |
| Source connectors | One module per source in `sources/`, implement `SourceConnector` protocol |
| Notification adapters | One module per channel in `notifications/`, implement `Notifier` protocol |
| Testing | pytest (backend), Vitest (frontend), fixtures over live calls |
| Commits | `tipo(ámbito): descripción`, pequeños, atómicos, **en español** |
| Secrets | Environment variables only, never committed |
| Every execution ends with | Exactamente 5 ideas de mejora **en español** |
| Assumptions | Stated explicitly, never treated as confirmed |
| AI guide files | `CLAUDE.md` (Claude Code) + `AGENTS.md` (Codex) — keep both in sync |
