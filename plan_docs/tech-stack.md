# Technology Stack

**Project:** workflow-orchestration-queue (OS-APOW)
**Last Updated:** 2026-03-26

---

## Languages

| Language | Version | Purpose |
|----------|---------|---------|
| Python | 3.12+ | Primary language for Orchestrator, API, and system logic |
| PowerShell Core (pwsh) | 7.x | Auth synchronization and cross-platform CLI (optional, for scripts) |
| Bash | 5.x | Shell Bridge scripts, container lifecycle management |

---

## Frameworks

| Framework | Version | Purpose |
|-----------|---------|---------|
| FastAPI | Latest | High-performance async web framework for webhook receiver |
| Uvicorn | Latest | ASGI server for FastAPI in production |
| Pydantic | 2.x | Data validation, settings management, schema definitions |

---

## Package Managers

| Tool | Version | Purpose |
|------|---------|---------|
| uv | 0.10+ | Rust-based Python package manager (primary) |
| pip | (via uv) | Fallback package installer |

---

## HTTP Client

| Library | Version | Purpose |
|---------|---------|---------|
| HTTPX | 0.27+ | Async HTTP client for GitHub REST API calls |

---

## Containerization

| Tool | Version | Purpose |
|------|---------|---------|
| Docker | 24+ | Container runtime for worker isolation |
| DevContainers | Latest | Reproducible development environment |

---

## LLM/Agent Runtime

| Tool | Version | Purpose |
|------|---------|---------|
| opencode CLI | 1.2.24 | AI agent runtime for executing workflows |
| ZhipuAI GLM | - | Primary LLM model (via ZHIPU_API_KEY) |

---

## MCP Servers

| Server | Purpose |
|--------|---------|
| @modelcontextprotocol/server-sequential-thinking | Step-by-step reasoning for complex problems |
| @modelcontextprotocol/server-memory | Knowledge graph persistence |

---

## Development Tools

| Tool | Purpose |
|------|---------|
| pytest | Unit testing framework |
| ruff | Fast Python linter and formatter |
| mypy | Static type checking |

---

## External Services

| Service | Purpose |
|---------|---------|
| GitHub REST API | Work queue (Issues with labels as state machine) |
| GitHub App | Webhook events, installation tokens |
| GitHub Actions | CI/CD pipeline |

---

## Key Dependencies (pyproject.toml)

```toml
[project]
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "httpx>=0.27.0",
]
```

---

## Version Pinning Strategy

- **Python version:** Pinned via `.python-version` file
- **Dependencies:** Pinned in `uv.lock` for reproducibility
- **GitHub Actions:** Pinned to full commit SHA (not version tags)

---

## Security Considerations

- All secrets via environment variables (never in code)
- Credential scrubbing before posting to GitHub
- HMAC signature validation on webhooks
- Ephemeral credentials in worker containers
