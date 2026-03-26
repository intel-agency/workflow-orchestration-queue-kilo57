"""Workflow Orchestration Queue - GitHub Actions-based AI orchestration system."""

from importlib.metadata import version

from workflow_orchestration_queue.models import (
    TaskType,
    WorkItem,
    WorkItemStatus,
    scrub_secrets,
)
from workflow_orchestration_queue.queue import GitHubQueue, ITaskQueue

__version__ = version("workflow-orchestration-queue")

__all__ = [
    "__version__",
    "TaskType",
    "WorkItemStatus",
    "WorkItem",
    "scrub_secrets",
    "ITaskQueue",
    "GitHubQueue",
]
