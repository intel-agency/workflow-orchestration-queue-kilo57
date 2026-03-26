"""Tests for workflow-orchestration-queue."""

import pytest

from src.models import TaskType, WorkItem, WorkItemStatus, scrub_secrets


class TestWorkItem:
    """Tests for the WorkItem model."""

    def test_task_type_enum_values(self) -> None:
        """Test that TaskType enum has expected values."""
        assert TaskType.PLAN.value == "PLAN"
        assert TaskType.IMPLEMENT.value == "IMPLEMENT"
        assert TaskType.BUGFIX.value == "BUGFIX"

    def test_work_item_status_enum_values(self) -> None:
        """Test that WorkItemStatus enum has expected values."""
        assert WorkItemStatus.QUEUED.value == "agent:queued"
        assert WorkItemStatus.IN_PROGRESS.value == "agent:in-progress"
        assert WorkItemStatus.SUCCESS.value == "agent:success"
        assert WorkItemStatus.ERROR.value == "agent:error"

    def test_work_item_creation(self) -> None:
        """Test creating a WorkItem instance."""
        item = WorkItem(
            id="123",
            issue_number=1,
            source_url="https://github.com/test/repo/issues/1",
            context_body="Test issue body",
            target_repo_slug="test/repo",
            task_type=TaskType.IMPLEMENT,
            status=WorkItemStatus.QUEUED,
            node_id="I_123",
        )
        assert item.id == "123"
        assert item.issue_number == 1
        assert item.task_type == TaskType.IMPLEMENT


class TestScrubSecrets:
    """Tests for the scrub_secrets function."""

    def test_scrub_github_pat(self) -> None:
        """Test that GitHub PATs are scrubbed."""
        text = "Token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        result = scrub_secrets(text)
        assert "ghp_" not in result
        assert "***REDACTED***" in result

    def test_scrub_bearer_token(self) -> None:
        """Test that Bearer tokens are scrubbed."""
        text = "Authorization: Bearer abc123def456"
        result = scrub_secrets(text)
        assert "Bearer abc123def456" not in result
        assert "***REDACTED***" in result

    def test_scrub_sk_prefix(self) -> None:
        """Test that OpenAI-style keys are scrubbed."""
        text = "API key: sk-1234567890abcdefghijklmnopqrstuvwxyz"
        result = scrub_secrets(text)
        assert "sk-" not in result
        assert "***REDACTED***" in result

    def test_no_secrets_to_scrub(self) -> None:
        """Test that normal text is unchanged."""
        text = "This is a normal log message with no secrets"
        result = scrub_secrets(text)
        assert result == text

    def test_custom_replacement(self) -> None:
        """Test custom replacement string."""
        text = "Token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        result = scrub_secrets(text, replacement="[HIDDEN]")
        assert "[HIDDEN]" in result
