# Workflow Execution Plan: project-setup

**Generated:** 2026-03-26
**Repository:** intel-agency/workflow-orchestration-queue-kilo57
**Workflow:** `project-setup` (dynamic workflow)

---

## 1. Overview

This document provides a comprehensive execution plan for the `project-setup` dynamic workflow. The workflow initializes the repository for the **workflow-orchestration-queue** (OS-APOW) project — a headless agentic orchestration platform that transforms GitHub Issues into automated execution orders.

**Project Description:** workflow-orchestration-queue is a groundbreaking platform that transforms "interactive" AI coding into an autonomous background production service. It uses a 4-pillar architecture (Ear/State/Brain/Hands) to detect work orders via GitHub Labels, claim tasks using distributed locking, and execute agentic workflows in isolated DevContainers.

**Total Assignments:** 5 main assignments + 2 post-assignment events each + 1 pre-script event + 1 post-script event

---

## 2. Project Context Summary

### Key Facts from `plan_docs/`

| Aspect | Details |
|--------|---------|
| **Project Name** | workflow-orchestration-queue (OS-APOW) |
| **Primary Language** | Python 3.12+ |
| **Frameworks** | FastAPI, Uvicorn, Pydantic, HTTPX |
| **Package Manager** | uv (Rust-based, fast dependency resolver) |
| **Containerization** | Docker, DevContainers |
| **Key Components** | Sentinel Orchestrator (polling daemon), Work Event Notifier (FastAPI webhooks), GitHub-backed work queue |
| **Repository** | intel-agency/workflow-orchestration-queue-kilo57 |

### Technology Stack

- **Python 3.12+** with async/await patterns
- **FastAPI** for webhook receiver
- **Pydantic** for data validation
- **HTTPX** for async HTTP client
- **uv** for package management
- **Docker/DevContainers** for worker isolation
- **Shell Bridge** (`devcontainer-opencode.sh`) for container lifecycle

### Architecture Highlights

1. **4-Pillar Architecture:** Ear (Notifier) / State (Queue) / Brain (Sentinel) / Hands (Worker)
2. **Polling-First Resiliency:** Webhooks are optimization; polling ensures self-healing
3. **Markdown-as-Database:** GitHub Issues as persistence layer with labels as state machine
4. **Shell-Bridge Execution:** All container ops via `devcontainer-opencode.sh` for environment parity
5. **Assign-Then-Verify Locking:** Distributed locking using GitHub Assignees

### Reference Implementations (in `plan_docs/`)

The `plan_docs/` directory contains reference implementations that were reviewed and refined:
- `src/models/work_item.py` — Unified data model
- `src/queue/github_queue.py` — GitHub-backed queue with connection pooling
- `orchestrator_sentinel.py` — Sentinel orchestrator reference
- `notifier_service.py` — FastAPI webhook receiver reference

### Known Risks

1. **Long-running subagent delegations** (15+ min) require heartbeat system
2. **Race conditions** require assign-then-verify locking pattern
3. **Rate limiting** requires jittered exponential backoff
4. **Secret leakage** requires credential scrubbing before posting to GitHub

---

## 3. Assignment Execution Plan

### Phase 1: Pre-script Event

| Field | Content |
|---|---|
| **Assignment** | `create-workflow-plan`: Create Workflow Plan |
| **Goal** | Create a comprehensive workflow execution plan before any other assignment begins |
| **Key Acceptance Criteria** | - Dynamic workflow fully read and all assignments traced<br>- All plan_docs/ files read and summarized<br>- Workflow execution plan covers every assignment in order<br>- Plan approved by stakeholder<br>- `plan_docs/workflow-plan.md` committed and pushed |
| **Project-Specific Notes** | This is a planning-only assignment. No code changes. The plan docs contain detailed architecture, implementation specs, and reference implementations that inform execution. |
| **Prerequisites** | None — this is the first assignment |
| **Dependencies** | None |
| **Risks / Challenges** | Ensuring all plan docs are read and understood; stakeholder alignment on execution order |
| **Events** | None |

---

### Phase 2: Main Assignments (Sequential)

#### Assignment 1: `init-existing-repository`

| Field | Content |
|---|---|
| **Assignment** | `init-existing-repository`: Initiate Existing Repository |
| **Goal** | Initialize repository configuration: create branch, import labels, create project, import branch protection ruleset |
| **Key Acceptance Criteria** | - New branch `dynamic-workflow-project-setup` created<br>- Branch protection ruleset imported from `.github/protected-branches_ruleset.json`<br>- GitHub Project created and linked<br>- Labels imported from `.github/.labels.json`<br>- Workspace/devcontainer files renamed to match project name<br>- PR created from branch to `main` |
| **Project-Specific Notes** | - Repository is `intel-agency/workflow-orchestration-queue-kilo57`<br>- Rename `ai-new-app-template.code-workspace` to `workflow-orchestration-queue-kilo57.code-workspace`<br>- Update devcontainer name to `workflow-orchestration-queue-kilo57-devcontainer`<br>- Use `scripts/import-labels.ps1` for label import |
| **Prerequisites** | `create-workflow-plan` completed |
| **Dependencies** | None |
| **Risks / Challenges** | - Requires `administration: write` scope for ruleset import<br>- May need `GH_ORCHESTRATION_AGENT_TOKEN` for ruleset API |
| **Events** | `post-assignment-complete` → `validate-assignment-completion`, `report-progress` |

---

#### Assignment 2: `create-app-plan`

| Field | Content |
|---|---|
| **Assignment** | `create-app-plan`: Create Application Plan |
| **Goal** | Create a comprehensive application plan documented as a GitHub Issue using the template |
| **Key Acceptance Criteria** | - Application template analyzed and understood<br>- Plan documented in GitHub Issue using Appendix A template<br>- Tech stack documented in `plan_docs/tech-stack.md`<br>- Architecture documented in `plan_docs/architecture.md`<br>- Milestones created and issues linked<br>- Issue added to GitHub Project<br>- Labels applied (planning, documentation) |
| **Project-Specific Notes** | - Primary app spec: `plan_docs/OS-APOW Implementation Specification v1.2.md`<br>- Supporting docs: Architecture Guide, Development Plan, Plan Review, Simplification Report<br>- Reference implementations already exist in `plan_docs/`<br>- **NO CODE IMPLEMENTATION** — planning only |
| **Prerequisites** | `init-existing-repository` completed |
| **Dependencies** | Branch from init assignment; GitHub Project from init assignment |
| **Risks / Challenges** | - Large scope (4 phases) requires careful breakdown<br>- Must distinguish MVP (Phase 1) from future work (Phases 2-3) |
| **Events** | `pre-assignment-begin` → `gather-context`<br>`on-assignment-failure` → `recover-from-error`<br>`post-assignment-complete` → `validate-assignment-completion`, `report-progress` |

---

#### Assignment 3: `create-project-structure`

| Field | Content |
|---|---|
| **Assignment** | `create-project-structure`: Create Project Structure |
| **Goal** | Create actual project scaffolding: solution structure, project files, Docker configs, CI/CD foundation, documentation |
| **Key Acceptance Criteria** | - Solution/project structure created per tech stack<br>- Dockerfile and docker-compose.yml created<br>- Development environment configured<br>- Documentation structure created<br>- CI/CD workflow foundation established<br>- Repository summary created<br>- All GitHub Actions pinned to full SHA<br>- Stakeholder approval obtained |
| **Project-Specific Notes** | - Tech stack: Python 3.12+, uv, FastAPI, Pydantic, HTTPX<br>- Structure should follow Implementation Spec §Project Structure<br>- Move reference implementations from `plan_docs/` to `src/`<br>- Create `pyproject.toml` for uv package management<br>- Use Python stdlib for Docker healthchecks (not curl) |
| **Prerequisites** | `create-app-plan` completed |
| **Dependencies** | Application plan issue; tech-stack.md; architecture.md |
| **Risks / Challenges** | - Large amount of file creation<br>- Must ensure all actions in workflows are SHA-pinned |
| **Events** | `post-assignment-complete` → `validate-assignment-completion`, `report-progress` |

---

#### Assignment 4: `create-agents-md-file`

| Field | Content |
|---|---|
| **Assignment** | `create-agents-md-file`: Create AGENTS.md File |
| **Goal** | Create comprehensive AGENTS.md file for AI coding agents with project context and instructions |
| **Key Acceptance Criteria** | - `AGENTS.md` exists at repository root<br>- Contains project overview, setup commands, structure, code style<br>- All commands validated by running them<br>- Complements README.md and `.ai-repository-summary.md`<br>- Committed and pushed to working branch |
| **Project-Specific Notes** | - This is a Python project with uv package manager<br>- Key commands: `uv sync`, `uv run pytest`, `uv run ruff check`<br>- Reference existing AGENTS.md from template as starting point<br>- Include shell bridge commands: `devcontainer-opencode.sh up/start/prompt` |
| **Prerequisites** | `create-project-structure` completed |
| **Dependencies** | Project structure; tech stack decisions |
| **Risks / Challenges** | - Commands must be validated — may need to adjust if structure changes |
| **Events** | `post-assignment-complete` → `validate-assignment-completion`, `report-progress` |

---

#### Assignment 5: `debrief-and-document`

| Field | Content |
|---|---|
| **Assignment** | `debrief-and-document`: Debrief and Document Learnings |
| **Goal** | Capture key learnings, insights, and areas for improvement from the workflow execution |
| **Key Acceptance Criteria** | - Detailed report created using structured template<br>- Report in .md format<br>- All deviations documented<br>- Report reviewed and approved<br>- Committed to repo<br>- Execution trace saved as `debrief-and-document/trace.md` |
| **Project-Specific Notes** | - Include findings about reference implementations<br>- Flag any plan-impacting discoveries<br>- Recommend updates to workflow assignments if needed |
| **Prerequisites** | All main assignments completed |
| **Dependencies** | All prior assignment outputs |
| **Risks / Challenges** | - Must be thorough in documenting deviations<br>- Action items must be specific and actionable |
| **Events** | `post-assignment-complete` → `validate-assignment-completion`, `report-progress` |

---

### Phase 3: Post-Assignment Events

After each main assignment completes:

| Event | Assignments |
|-------|-------------|
| `post-assignment-complete` | `validate-assignment-completion` → `report-progress` |

#### `validate-assignment-completion`

- Verify all acceptance criteria met
- Run verification commands (build, test, lint)
- Create validation report
- Block progression if failed

#### `report-progress`

- Generate structured progress report
- Capture step outputs
- Create checkpoint state
- Notify user for long-running workflows

---

### Phase 4: Post-script Event

| Field | Content |
|---|---|
| **Event** | `post-script-complete` |
| **Action** | Apply `orchestration:plan-approved` label to the Application Plan issue |
| **Goal** | Signal that the plan is ready for epic creation |
| **Dependencies** | Application Plan issue number from `create-app-plan` assignment |

---

## 4. Sequencing Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        project-setup Workflow                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Phase 1: Pre-script                                                          │
│ ┌─────────────────────────┐                                                  │
│ │ create-workflow-plan    │ → plan_docs/workflow-plan.md                    │
│ └─────────────────────────┘                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Phase 2: Main Assignments (sequential)                                       │
│                                                                              │
│ ┌─────────────────────────┐     ┌─────────────────────────┐                 │
│ │ init-existing-repo      │ ──▶ │ create-app-plan         │                 │
│ └─────────────────────────┘     └─────────────────────────┘                 │
│          │                                │                                  │
│          ▼                                ▼                                  │
│ ┌─────────────────────────┐     ┌─────────────────────────┐                 │
│ │ validate-assignment     │     │ validate-assignment     │                 │
│ │ report-progress         │     │ report-progress         │                 │
│ └─────────────────────────┘     └─────────────────────────┘                 │
│                                          │                                   │
│                                          ▼                                   │
│                              ┌─────────────────────────┐                    │
│                              │ create-project-structure│                    │
│                              └─────────────────────────┘                    │
│                                          │                                   │
│                                          ▼                                   │
│                              ┌─────────────────────────┐                    │
│                              │ validate-assignment     │                    │
│                              │ report-progress         │                    │
│                              └─────────────────────────┘                    │
│                                          │                                   │
│                                          ▼                                   │
│                              ┌─────────────────────────┐                    │
│                              │ create-agents-md-file   │                    │
│                              └─────────────────────────┘                    │
│                                          │                                   │
│                                          ▼                                   │
│                              ┌─────────────────────────┐                    │
│                              │ validate-assignment     │                    │
│                              │ report-progress         │                    │
│                              └─────────────────────────┘                    │
│                                          │                                   │
│                                          ▼                                   │
│                              ┌─────────────────────────┐                    │
│                              │ debrief-and-document    │                    │
│                              └─────────────────────────┘                    │
│                                          │                                   │
│                                          ▼                                   │
│                              ┌─────────────────────────┐                    │
│                              │ validate-assignment     │                    │
│                              │ report-progress         │                    │
│                              └─────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Phase 4: Post-script                                                         │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Apply orchestration:plan-approved label to Application Plan issue       │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Open Questions

1. **Branch Protection Ruleset Import:** Does the PAT have `administration: write` scope? If not, the ruleset import step may fail. Alternative: manually configure via GitHub UI.

2. **Application Plan Scope:** Should the plan include Phase 2 and Phase 3 as future work, or focus only on Phase 1 (MVP)? The plan docs suggest including them but marking as deferred.

3. **Reference Implementation Migration:** Should the reference implementations in `plan_docs/src/` be moved to the actual `src/` directory during `create-project-structure`, or should fresh scaffolding be created? Recommendation: Move and adapt the reference implementations.

---

## 6. Execution Status Tracking

| Assignment | Status | Issue/Output | Notes |
|------------|--------|--------------|-------|
| create-workflow-plan | ✅ Complete | `plan_docs/workflow-plan.md` | This document |
| init-existing-repository | ⏳ Pending | - | - |
| create-app-plan | ⏳ Pending | - | - |
| create-project-structure | ⏳ Pending | - | - |
| create-agents-md-file | ⏳ Pending | - | - |
| debrief-and-document | ⏳ Pending | - | - |
| post-script-complete | ⏳ Pending | - | Apply `orchestration:plan-approved` label |

---

*This plan is ready for stakeholder review and approval before proceeding with execution.*
