"""OS-APOW Unified Work Item Model.

Canonical data model shared by both the Sentinel Orchestrator and the
Work Event Notifier. Both components import from this module to prevent
model divergence.

See:
    - ADR 09: Task Queue Abstraction
    - OS-APOW Plan Review, I-1 / R-3
"""

import re
from enum import StrEnum

from pydantic import BaseModel


class TaskType(StrEnum):
    """The kind of work the agent should perform.

    Used to categorize work items for appropriate handling by the
    Sentinel Orchestrator.
    """

    PLAN = "PLAN"
    IMPLEMENT = "IMPLEMENT"
    BUGFIX = "BUGFIX"


class WorkItemStatus(StrEnum):
    """Maps directly to GitHub Issue labels used as state indicators.

    These status values correspond to GitHub labels that track the
    lifecycle of a work item through the orchestration system.
    """

    QUEUED = "agent:queued"
    IN_PROGRESS = "agent:in-progress"
    RECONCILING = "agent:reconciling"
    SUCCESS = "agent:success"
    ERROR = "agent:error"
    INFRA_FAILURE = "agent:infra-failure"
    STALLED_BUDGET = "agent:stalled-budget"


class WorkItem(BaseModel):
    """Unified work item used across all OS-APOW components.

    Fields populated by the Notifier are marked Optional so the Sentinel
    can construct WorkItems from its own polling results without requiring
    the raw webhook payload.

    Attributes:
        id: Unique identifier for the work item (GitHub issue ID).
        issue_number: GitHub issue number for human-readable reference.
        source_url: Full URL to the source GitHub issue.
        context_body: The body text of the issue containing task context.
        target_repo_slug: Repository slug in 'owner/repo' format.
        task_type: Classification of the work (PLAN, IMPLEMENT, BUGFIX).
        status: Current status in the orchestration lifecycle.
        node_id: GraphQL node ID for GitHub API operations.

    """

    id: str
    issue_number: int
    source_url: str
    context_body: str
    target_repo_slug: str
    task_type: TaskType
    status: WorkItemStatus
    node_id: str


# --- Credential Scrubber (R-7) ---
# Regex patterns that match common secret formats. Used to sanitize
# worker output before posting to GitHub issue comments.
# IMPORTANT: These patterns must be kept in sync with security requirements.

_SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9_]{36,}"),  # GitHub PAT (classic)
    re.compile(r"ghs_[A-Za-z0-9_]{36,}"),  # GitHub App installation token
    re.compile(r"gho_[A-Za-z0-9_]{36,}"),  # GitHub OAuth token
    re.compile(r"github_pat_[A-Za-z0-9_]{22,}"),  # GitHub fine-grained PAT
    re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),
    re.compile(r"token\s+[A-Za-z0-9\-._~+/]{20,}", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),  # OpenAI-style API keys
    re.compile(r"[A-Za-z0-9]{32,}\.zhipu[A-Za-z0-9]*"),  # ZhipuAI keys
]


def scrub_secrets(text: str, replacement: str = "***REDACTED***") -> str:
    """Strip known secret patterns from text for safe public posting.

    This function is critical for security requirement R-7 in the
    OS-APOW Plan Review, ensuring that sensitive credentials are never
    exposed in GitHub issue comments or logs.

    Args:
        text: The input text potentially containing secrets.
        replacement: The string to replace secrets with. Defaults to
            '***REDACTED***'.

    Returns:
        The sanitized text with all matching secret patterns replaced.

    Example:
        >>> scrub_secrets("Token: ghp_abc123...")
        'Token: ***REDACTED***'

    """
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text
