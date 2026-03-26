# Architecture Overview

**Project:** workflow-orchestration-queue (OS-APOW)
**Last Updated:** 2026-03-26

---

## Executive Summary

workflow-orchestration-queue (OS-APOW) is a headless agentic orchestration platform that transforms standard project management artifacts (GitHub Issues) into automated Execution Orders. It shifts AI from a passive co-pilot role to an autonomous background production service.

---

## 4-Pillar Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            GitHub (External)                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Issues    │  │   Labels    │  │  Webhooks   │  │    API      │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          OS-APOW System                                      │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │              EAR: Work Event Notifier (FastAPI)                       │   │
│  │  • Secure webhook ingestion (HMAC SHA256 validation)                  │   │
│  │  • Intelligent event triaging (template detection)                    │   │
│  │  • WorkItem manifest generation                                       │   │
│  │  • Queue initialization (agent:queued label)                          │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │              STATE: Work Queue (GitHub Issues)                        │   │
│  │  • "Markdown as a Database" philosophy                                │   │
│  │  • Labels as state machine: queued → in-progress → success/error      │   │
│  │  • Assignees as distributed lock (assign-then-verify)                 │   │
│  │  • Full audit trail via GitHub UI                                     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │              BRAIN: Sentinel Orchestrator (Async Python)              │   │
│  │  • Persistent polling (60s interval, jittered exponential backoff)    │   │
│  │  • Distributed locking via assign-then-verify pattern                 │   │
│  │  • Shell-Bridge dispatch (devcontainer-opencode.sh)                   │   │
│  │  • Heartbeat posting (5 min intervals)                                │   │
│  │  • Graceful shutdown (SIGTERM/SIGINT handling)                        │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │              HANDS: Opencode Worker (DevContainer)                    │   │
│  │  • Isolated Docker environment                                        │   │
│  │  • LLM-driven agent (GLM-5 via ZhipuAI)                               │   │
│  │  • Markdown-based instruction modules                                  │   │
│  │  • Vector-indexed codebase awareness                                  │   │
│  │  • Local test verification before PR                                  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. The Ear (Work Event Notifier)

**File:** `src/notifier_service.py`

| Aspect | Details |
|--------|---------|
| **Technology** | FastAPI, Uvicorn, Pydantic |
| **Port** | 8000 (configurable) |
| **Endpoints** | `/webhooks/github`, `/health` |
| **Security** | HMAC SHA256 signature validation |

**Responsibilities:**
- Secure webhook ingestion from GitHub App
- Cryptographic verification of all incoming requests
- Intelligent event triaging based on issue templates
- WorkItem manifest generation
- Queue initialization via `agent:queued` label

### 2. The State (Work Queue)

**Implementation:** GitHub Issues + Labels

| Label | State | Description |
|-------|-------|-------------|
| `agent:queued` | QUEUED | Awaiting available Sentinel |
| `agent:in-progress` | IN_PROGRESS | Claimed by a Sentinel |
| `agent:reconciling` | RECONCILING | Stale task being recovered |
| `agent:success` | SUCCESS | Terminal success state |
| `agent:error` | ERROR | Execution error |
| `agent:infra-failure` | INFRA_FAILURE | Container/infrastructure error |
| `agent:stalled-budget` | STALLED_BUDGET | Budget limit exceeded |

**Concurrency Control:**
- Uses GitHub Assignees as distributed semaphore
- Assign-then-verify pattern prevents race conditions
- `SENTINEL_BOT_LOGIN` env var identifies bot account

### 3. The Brain (Sentinel Orchestrator)

**File:** `src/orchestrator_sentinel.py`

| Aspect | Details |
|--------|---------|
| **Technology** | Python 3.12+, asyncio |
| **Polling Interval** | 60 seconds (configurable) |
| **Max Backoff** | 960 seconds (16 min) |
| **Heartbeat Interval** | 300 seconds (5 min) |
| **Subprocess Timeout** | 5700 seconds (95 min) |

**Responsibilities:**
- Poll GitHub for `agent:queued` issues
- Claim tasks using assign-then-verify locking
- Manage worker lifecycle via Shell Bridge
- Post heartbeat comments during long-running tasks
- Handle graceful shutdown on SIGTERM/SIGINT

**Shell Bridge Commands:**
1. `devcontainer-opencode.sh up` — Initialize infrastructure
2. `devcontainer-opencode.sh start` — Start opencode server
3. `devcontainer-opencode.sh prompt "<instruction>"` — Execute workflow
4. `devcontainer-opencode.sh stop` — Stop container between tasks

### 4. The Hands (Opencode Worker)

**Environment:** DevContainer (Docker)

| Aspect | Details |
|--------|---------|
| **Base Image** | ghcr.io/intel-agency/workflow-orchestration-prebuild/devcontainer |
| **Runtime** | opencode CLI (v1.2.24) |
| **LLM** | ZhipuAI GLM-5 |
| **Resource Limits** | 2 CPUs, 4GB RAM |

**Responsibilities:**
- Execute markdown-based instruction modules
- Maintain vector-indexed codebase awareness
- Run local tests before submitting PRs
- Generate code across multiple files
- Submit formatted Pull Requests

---

## Key Architectural Decisions (ADRs)

### ADR 07: Standardized Shell-Bridge Execution

**Decision:** Orchestrator interacts with worker exclusively via `devcontainer-opencode.sh`

**Rationale:**
- Guarantees environment parity between AI and human developers
- Avoids "Configuration Drift"
- Keeps Python layer focused on logic/state

### ADR 08: Polling-First Resiliency Model

**Decision:** Polling as primary discovery; webhooks as optimization

**Rationale:**
- Webhooks are "fire and forget" — events lost if server is down
- Polling enables "State Reconciliation" on restart
- System is inherently self-healing

### ADR 09: Provider-Agnostic Interface Layer

**Decision:** All queue interactions abstracted behind `ITaskQueue` interface

**Rationale:**
- Enables future support for Linear, Notion, or SQL queues
- No orchestrator logic rewrite needed for provider swap
- Strategy Pattern for queue implementations

---

## Data Flow (Happy Path)

```
1. User opens GitHub Issue with [Application Plan] template
2. Webhook hits Notifier (FastAPI)
3. Notifier verifies signature, confirms template, adds agent:queued label
4. Sentinel poller detects new label
5. Sentinel assigns itself, updates to agent:in-progress
6. Sentinel runs git pull to sync workspace
7. Sentinel executes: devcontainer-opencode.sh up
8. Sentinel dispatches: devcontainer-opencode.sh prompt "Run workflow..."
9. Worker executes workflow, creates child issues, submits PR
10. Worker posts completion comment
11. Sentinel removes in-progress, adds agent:success
```

---

## Security Model

### Network Isolation
- Worker containers in dedicated Docker network
- Cannot access host network or local subnet
- Internet access for packages only

### Credential Scoping
- GitHub Installation Tokens injected as temp env vars
- Variables destroyed on container exit
- Least privilege model

### Credential Scrubbing
- Regex-based scrubber (`scrub_secrets()`) in `src/models/work_item.py`
- Strips patterns: `ghp_*`, `ghs_*`, `gho_*`, `github_pat_*`, `Bearer`, `sk-*`, ZhipuAI keys
- Applied before posting any worker output to GitHub

### Resource Constraints
- Hard limits: 2 CPUs, 4GB RAM per worker
- Prevents "rogue agent" DoS scenarios

---

## Directory Structure

```
workflow-orchestration-queue/
├── pyproject.toml               # Core definition file for uv
├── uv.lock                      # Deterministic lockfile
├── src/
│   ├── notifier_service.py      # FastAPI webhook receiver
│   ├── orchestrator_sentinel.py # Background polling daemon
│   ├── models/
│   │   ├── work_item.py         # Unified WorkItem, TaskType, scrub_secrets()
│   │   └── github_events.py     # GitHub webhook payload schemas
│   └── queue/
│       └── github_queue.py      # ITaskQueue + GitHubQueue
├── scripts/
│   ├── devcontainer-opencode.sh # Shell Bridge for worker lifecycle
│   ├── gh-auth.ps1              # GitHub auth helper
│   └── update-remote-indices.ps1# Vector index sync
├── local_ai_instruction_modules/# Markdown-based agent instructions
└── docs/                        # Architecture and user documentation
```

---

## Self-Bootstrapping Lifecycle

1. **Bootstrap:** Developer clones template repo
2. **Seed:** Add plan docs to repo
3. **Init:** Run `devcontainer-opencode.sh up`
4. **Orchestrate:** Execute `project-setup` workflow
5. **Autonomous:** Start Sentinel service; AI manages all further development

---

## Future Phases

### Phase 2: The Ear (Webhook Automation)
- Sub-second task ingestion
- Template-based auto-labeling
- Local tunneling for development

### Phase 3: Deep Orchestration
- Architect Sub-Agent for epic decomposition
- Autonomous PR review corrections
- Dynamic workspace vector indexing

See "Appendix: Future Work" in Implementation Specification for details.
