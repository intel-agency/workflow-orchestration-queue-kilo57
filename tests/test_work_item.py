"""Unit tests for WorkItem model and scrub_secrets function.

IMPORTANT: Test fixtures use synthetic values that won't trigger gitleaks.
Pattern: FAKE-KEY-FOR-TESTING-00000000 (NOT ghp_, sk_, etc.)
"""

import pytest

from workflow_orchestration_queue.models import (
    TaskType,
    WorkItem,
    WorkItemStatus,
    scrub_secrets,
)


class TestTaskType:
    """Tests for TaskType enum."""

    def test_task_type_plan(self) -> None:
        """Test PLAN enum value."""
        assert TaskType.PLAN.value == "PLAN"

    def test_task_type_implement(self) -> None:
        """Test IMPLEMENT enum value."""
        assert TaskType.IMPLEMENT.value == "IMPLEMENT"

    def test_task_type_bugfix(self) -> None:
        """Test BUGFIX enum value."""
        assert TaskType.BUGFIX.value == "BUGFIX"

    def test_task_type_count(self) -> None:
        """Verify we have exactly 3 task types."""
        assert len(TaskType) == 3

    def test_task_type_is_string_enum(self) -> None:
        """Verify TaskType is a string enum."""
        assert isinstance(TaskType.PLAN, str)
        assert TaskType.PLAN == "PLAN"


class TestWorkItemStatus:
    """Tests for WorkItemStatus enum."""

    def test_status_queued(self) -> None:
        """Test QUEUED status maps to agent:queued label."""
        assert WorkItemStatus.QUEUED.value == "agent:queued"

    def test_status_in_progress(self) -> None:
        """Test IN_PROGRESS status maps to agent:in-progress label."""
        assert WorkItemStatus.IN_PROGRESS.value == "agent:in-progress"

    def test_status_reconciling(self) -> None:
        """Test RECONCILING status."""
        assert WorkItemStatus.RECONCILING.value == "agent:reconciling"

    def test_status_success(self) -> None:
        """Test SUCCESS status."""
        assert WorkItemStatus.SUCCESS.value == "agent:success"

    def test_status_error(self) -> None:
        """Test ERROR status."""
        assert WorkItemStatus.ERROR.value == "agent:error"

    def test_status_infra_failure(self) -> None:
        """Test INFRA_FAILURE status."""
        assert WorkItemStatus.INFRA_FAILURE.value == "agent:infra-failure"

    def test_status_stalled_budget(self) -> None:
        """Test STALLED_BUDGET status."""
        assert WorkItemStatus.STALLED_BUDGET.value == "agent:stalled-budget"

    def test_status_count(self) -> None:
        """Verify we have exactly 7 status values."""
        assert len(WorkItemStatus) == 7


class TestWorkItem:
    """Tests for WorkItem model."""

    @pytest.fixture
    def sample_work_item(self) -> WorkItem:
        """Provide a sample WorkItem for testing."""
        return WorkItem(
            id="123456789",
            issue_number=42,
            source_url="https://github.com/owner/repo/issues/42",
            context_body="Implement feature X",
            target_repo_slug="owner/repo",
            task_type=TaskType.IMPLEMENT,
            status=WorkItemStatus.QUEUED,
            node_id="I_kwDOABC123",
        )

    def test_work_item_instantiation(self, sample_work_item: WorkItem) -> None:
        """Test WorkItem can be instantiated with valid data."""
        assert sample_work_item.id == "123456789"
        assert sample_work_item.issue_number == 42
        assert sample_work_item.source_url == "https://github.com/owner/repo/issues/42"
        assert sample_work_item.context_body == "Implement feature X"
        assert sample_work_item.target_repo_slug == "owner/repo"
        assert sample_work_item.task_type == TaskType.IMPLEMENT
        assert sample_work_item.status == WorkItemStatus.QUEUED
        assert sample_work_item.node_id == "I_kwDOABC123"

    def test_work_item_with_plan_type(self) -> None:
        """Test WorkItem with PLAN task type."""
        item = WorkItem(
            id="1",
            issue_number=1,
            source_url="https://github.com/org/repo/issues/1",
            context_body="Plan the architecture",
            target_repo_slug="org/repo",
            task_type=TaskType.PLAN,
            status=WorkItemStatus.QUEUED,
            node_id="node_1",
        )
        assert item.task_type == TaskType.PLAN

    def test_work_item_with_bugfix_type(self) -> None:
        """Test WorkItem with BUGFIX task type."""
        item = WorkItem(
            id="2",
            issue_number=2,
            source_url="https://github.com/org/repo/issues/2",
            context_body="Fix the bug",
            target_repo_slug="org/repo",
            task_type=TaskType.BUGFIX,
            status=WorkItemStatus.IN_PROGRESS,
            node_id="node_2",
        )
        assert item.task_type == TaskType.BUGFIX

    def test_work_item_model_dump(self, sample_work_item: WorkItem) -> None:
        """Test WorkItem serialization via model_dump."""
        data = sample_work_item.model_dump()
        assert data["id"] == "123456789"
        assert data["issue_number"] == 42
        assert data["task_type"] == TaskType.IMPLEMENT
        assert data["status"] == WorkItemStatus.QUEUED

    def test_work_item_model_json(self, sample_work_item: WorkItem) -> None:
        """Test WorkItem JSON serialization."""
        json_str = sample_work_item.model_dump_json()
        assert '"id":"123456789"' in json_str
        assert '"issue_number":42' in json_str


class TestScrubSecrets:
    """Tests for scrub_secrets function.

    Uses synthetic test patterns that won't trigger gitleaks.
    Pattern: FAKE-KEY-FOR-TESTING-00000000
    """

    def test_scrub_secrets_no_secrets(self) -> None:
        """Test text without secrets passes through unchanged."""
        text = "This is a normal log message with no secrets."
        assert scrub_secrets(text) == text

    def test_scrub_secrets_empty_string(self) -> None:
        """Test empty string returns empty string."""
        assert scrub_secrets("") == ""

    def test_scrub_secrets_bearer_token(self) -> None:
        """Test Bearer token is redacted."""
        # Using synthetic pattern that matches Bearer regex
        text = "Authorization: Bearer FAKE-TOKEN-FOR-TESTING-1234567890AB=="
        result = scrub_secrets(text)
        assert "***REDACTED***" in result
        assert "FAKE-TOKEN" not in result

    def test_scrub_secrets_token_keyword(self) -> None:
        """Test 'token' keyword with long value is redacted."""
        # Using synthetic pattern that matches token regex
        text = "token FAKE-TOKEN-FOR-TESTING-12345678"
        result = scrub_secrets(text)
        assert "***REDACTED***" in result

    def test_scrub_secrets_multiple_secrets(self) -> None:
        """Test multiple secrets in same text are all redacted."""
        text = (
            "Found Bearer FAKE-BEARER-123== and token FAKE-TOKEN-12345678901234567890"
        )
        result = scrub_secrets(text)
        assert result.count("***REDACTED***") == 2

    def test_scrub_secrets_custom_replacement(self) -> None:
        """Test custom replacement string."""
        text = "Bearer FAKE-BEARER-123=="
        result = scrub_secrets(text, replacement="[HIDDEN]")
        assert "[HIDDEN]" in result
        assert "***REDACTED***" not in result

    def test_scrub_secrets_preserves_structure(self) -> None:
        """Test that non-secret parts of text are preserved."""
        text = "Config: api_key=Bearer FAKE-BEARER-123==, timeout=30"
        result = scrub_secrets(text)
        assert "Config:" in result
        assert "timeout=30" in result

    def test_scrub_secrets_case_insensitive_bearer(self) -> None:
        """Test Bearer matching is case insensitive."""
        text_lower = "bearer FAKE-BEARER-123=="
        text_upper = "BEARER FAKE-BEARER-123=="
        text_mixed = "BeArEr FAKE-BEARER-123=="

        assert "***REDACTED***" in scrub_secrets(text_lower)
        assert "***REDACTED***" in scrub_secrets(text_upper)
        assert "***REDACTED***" in scrub_secrets(text_mixed)

    def test_scrub_secrets_case_insensitive_token(self) -> None:
        """Test token keyword matching is case insensitive."""
        text_lower = "token FAKE-TOKEN-12345678901234567890"
        text_upper = "TOKEN FAKE-TOKEN-12345678901234567890"
        text_mixed = "ToKeN FAKE-TOKEN-12345678901234567890"

        assert "***REDACTED***" in scrub_secrets(text_lower)
        assert "***REDACTED***" in scrub_secrets(text_upper)
        assert "***REDACTED***" in scrub_secrets(text_mixed)

    def test_scrub_secrets_zhipuai_pattern(self) -> None:
        """Test ZhipuAI key pattern (32+ chars followed by .zhipu)."""
        # Synthetic pattern matching ZhipuAI format
        text = "API Key: 12345678901234567890123456789012.zhipuABC"
        result = scrub_secrets(text)
        assert "***REDACTED***" in result

    def test_scrub_secrets_multiline_text(self) -> None:
        """Test secrets are redacted in multiline text."""
        text = """Configuration file:
        Bearer FAKE-BEARER-123==
        Other setting: value
        token FAKE-TOKEN-12345678901234567890
        End of config"""
        result = scrub_secrets(text)
        assert result.count("***REDACTED***") == 2
        assert "Other setting: value" in result

    def test_scrub_secrets_json_content(self) -> None:
        """Test secrets are redacted in JSON-like content."""
        text = '{"auth": "Bearer FAKE-BEARER-123==", "timeout": 30}'
        result = scrub_secrets(text)
        assert "***REDACTED***" in result
        assert '"timeout": 30' in result
