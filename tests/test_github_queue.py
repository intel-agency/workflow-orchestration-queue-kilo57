"""Unit tests for GitHubQueue implementation.

Uses mocked HTTPX client to test queue operations without actual GitHub API calls.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from workflow_orchestration_queue.models import (
    TaskType,
    WorkItem,
    WorkItemStatus,
)
from workflow_orchestration_queue.queue import GitHubQueue, ITaskQueue


class TestITaskQueueInterface:
    """Tests for ITaskQueue abstract interface compliance."""

    def test_itaskqueue_is_abstract(self) -> None:
        """Verify ITaskQueue cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ITaskQueue()  # type: ignore[abstract]

    def test_itaskqueue_has_add_to_queue_method(self) -> None:
        """Verify add_to_queue is an abstract method."""
        assert hasattr(ITaskQueue, "add_to_queue")
        assert callable(ITaskQueue.add_to_queue)

    def test_itaskqueue_has_fetch_queued_tasks_method(self) -> None:
        """Verify fetch_queued_tasks is an abstract method."""
        assert hasattr(ITaskQueue, "fetch_queued_tasks")
        assert callable(ITaskQueue.fetch_queued_tasks)

    def test_itaskqueue_has_update_status_method(self) -> None:
        """Verify update_status is an abstract method."""
        assert hasattr(ITaskQueue, "update_status")
        assert callable(ITaskQueue.update_status)

    def test_github_queue_implements_itaskqueue(self) -> None:
        """Verify GitHubQueue is a subclass of ITaskQueue."""
        assert issubclass(GitHubQueue, ITaskQueue)


class TestGitHubQueueInit:
    """Tests for GitHubQueue initialization."""

    def test_init_with_token_only(self) -> None:
        """Test initialization with token only."""
        queue = GitHubQueue(token="test-token")
        assert queue.token == "test-token"
        assert queue.org == ""
        assert queue.repo == ""

    def test_init_with_org_and_repo(self) -> None:
        """Test initialization with org and repo."""
        queue = GitHubQueue(token="test-token", org="myorg", repo="myrepo")
        assert queue.token == "test-token"
        assert queue.org == "myorg"
        assert queue.repo == "myrepo"

    def test_headers_are_set(self) -> None:
        """Test authorization headers are properly set."""
        queue = GitHubQueue(token="test-token")
        assert queue.headers["Authorization"] == "token test-token"
        assert queue.headers["Accept"] == "application/vnd.github.v3+json"

    def test_client_is_created(self) -> None:
        """Test HTTPX client is created with correct settings."""
        queue = GitHubQueue(token="test-token")
        assert isinstance(queue._client, httpx.AsyncClient)
        assert queue._client.timeout.read == 30.0


class TestGitHubQueueClose:
    """Tests for GitHubQueue.close method."""

    @pytest.mark.asyncio
    async def test_close_acloses_client(self) -> None:
        """Test close properly closes the HTTPX client."""
        queue = GitHubQueue(token="test-token")

        with patch.object(
            queue._client, "aclose", new_callable=AsyncMock
        ) as mock_aclose:
            await queue.close()
            mock_aclose.assert_called_once()


class TestGitHubQueueAddToQueue:
    """Tests for GitHubQueue.add_to_queue method."""

    @pytest.fixture
    def sample_work_item(self) -> WorkItem:
        """Provide a sample WorkItem for testing."""
        return WorkItem(
            id="123",
            issue_number=42,
            source_url="https://github.com/owner/repo/issues/42",
            context_body="Test task",
            target_repo_slug="owner/repo",
            task_type=TaskType.IMPLEMENT,
            status=WorkItemStatus.QUEUED,
            node_id="node_123",
        )

    @pytest.mark.asyncio
    async def test_add_to_queue_success(self, sample_work_item: WorkItem) -> None:
        """Test successful add_to_queue returns True."""
        queue = GitHubQueue(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 201

        with patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await queue.add_to_queue(sample_work_item)

            assert result is True
            mock_post.assert_called_once()
            # Verify URL contains correct issue number
            call_url = mock_post.call_args[0][0]
            assert "/issues/42/labels" in call_url

    @pytest.mark.asyncio
    async def test_add_to_queue_success_200(self, sample_work_item: WorkItem) -> None:
        """Test add_to_queue returns True on 200 status."""
        queue = GitHubQueue(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await queue.add_to_queue(sample_work_item)
            assert result is True

    @pytest.mark.asyncio
    async def test_add_to_queue_failure(self, sample_work_item: WorkItem) -> None:
        """Test add_to_queue returns False on non-success status."""
        queue = GitHubQueue(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await queue.add_to_queue(sample_work_item)
            assert result is False

    @pytest.mark.asyncio
    async def test_add_to_queue_posts_correct_label(
        self, sample_work_item: WorkItem
    ) -> None:
        """Test add_to_queue posts the correct label."""
        queue = GitHubQueue(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 201

        with patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            await queue.add_to_queue(sample_work_item)

            # Verify the JSON payload contains the correct label
            call_json = mock_post.call_args[1]["json"]
            assert call_json == {"labels": ["agent:queued"]}


class TestGitHubQueueFetchQueuedTasks:
    """Tests for GitHubQueue.fetch_queued_tasks method."""

    @pytest.mark.asyncio
    async def test_fetch_queued_tasks_requires_org_and_repo(self) -> None:
        """Test fetch_queued_tasks returns empty list without org/repo."""
        queue = GitHubQueue(token="test-token", org="", repo="")

        result = await queue.fetch_queued_tasks()
        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_queued_tasks_returns_empty_on_error(self) -> None:
        """Test fetch_queued_tasks returns empty list on API error."""
        queue = GitHubQueue(token="test-token", org="myorg", repo="myrepo")

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch.object(queue._client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            result = await queue.fetch_queued_tasks()
            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_queued_tasks_raises_on_rate_limit(self) -> None:
        """Test fetch_queued_tasks raises on rate limit (403/429)."""
        queue = GitHubQueue(token="test-token", org="myorg", repo="myrepo")

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Rate limited", request=MagicMock(), response=mock_response
        )

        with patch.object(queue._client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            with pytest.raises(httpx.HTTPStatusError):
                await queue.fetch_queued_tasks()

    @pytest.mark.asyncio
    async def test_fetch_queued_tasks_parses_issues(self) -> None:
        """Test fetch_queued_tasks correctly parses GitHub issues."""
        queue = GitHubQueue(token="test-token", org="myorg", repo="myrepo")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 12345,
                "number": 1,
                "html_url": "https://github.com/myorg/myrepo/issues/1",
                "body": "Test issue body",
                "labels": [{"name": "agent:queued"}],
                "node_id": "node_123",
            }
        ]

        with patch.object(queue._client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            items = await queue.fetch_queued_tasks()

            assert len(items) == 1
            assert items[0].id == "12345"
            assert items[0].issue_number == 1
            assert items[0].target_repo_slug == "myorg/myrepo"
            assert items[0].task_type == TaskType.IMPLEMENT

    @pytest.mark.asyncio
    async def test_fetch_queued_tasks_detects_plan_type(self) -> None:
        """Test fetch_queued_tasks detects PLAN task type from labels."""
        queue = GitHubQueue(token="test-token", org="myorg", repo="myrepo")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 123,
                "number": 2,
                "html_url": "https://github.com/myorg/myrepo/issues/2",
                "body": "Plan task",
                "labels": [{"name": "agent:plan"}],
                "node_id": "node_plan",
                "title": "Some task",
            }
        ]

        with patch.object(queue._client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            items = await queue.fetch_queued_tasks()
            assert items[0].task_type == TaskType.PLAN

    @pytest.mark.asyncio
    async def test_fetch_queued_tasks_detects_plan_from_title(self) -> None:
        """Test fetch_queued_tasks detects PLAN task type from title."""
        queue = GitHubQueue(token="test-token", org="myorg", repo="myrepo")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 124,
                "number": 3,
                "html_url": "https://github.com/myorg/myrepo/issues/3",
                "body": "Task",
                "labels": [{"name": "agent:queued"}],
                "node_id": "node_plan2",
                "title": "[Plan] Architecture design",
            }
        ]

        with patch.object(queue._client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            items = await queue.fetch_queued_tasks()
            assert items[0].task_type == TaskType.PLAN

    @pytest.mark.asyncio
    async def test_fetch_queued_tasks_detects_bugfix_type(self) -> None:
        """Test fetch_queued_tasks detects BUGFIX task type from labels."""
        queue = GitHubQueue(token="test-token", org="myorg", repo="myrepo")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 125,
                "number": 4,
                "html_url": "https://github.com/myorg/myrepo/issues/4",
                "body": "Bug fix",
                "labels": [{"name": "bug"}, {"name": "agent:queued"}],
                "node_id": "node_bug",
                "title": "Fix the thing",
            }
        ]

        with patch.object(queue._client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            items = await queue.fetch_queued_tasks()
            assert items[0].task_type == TaskType.BUGFIX

    @pytest.mark.asyncio
    async def test_fetch_queued_tasks_handles_none_body(self) -> None:
        """Test fetch_queued_tasks handles None body gracefully."""
        queue = GitHubQueue(token="test-token", org="myorg", repo="myrepo")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 126,
                "number": 5,
                "html_url": "https://github.com/myorg/myrepo/issues/5",
                "body": None,
                "labels": [{"name": "agent:queued"}],
                "node_id": "node_none",
            }
        ]

        with patch.object(queue._client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            items = await queue.fetch_queued_tasks()
            assert items[0].context_body == ""


class TestGitHubQueueUpdateStatus:
    """Tests for GitHubQueue.update_status method."""

    @pytest.fixture
    def sample_work_item(self) -> WorkItem:
        """Provide a sample WorkItem for testing."""
        return WorkItem(
            id="123",
            issue_number=42,
            source_url="https://github.com/owner/repo/issues/42",
            context_body="Test task",
            target_repo_slug="owner/repo",
            task_type=TaskType.IMPLEMENT,
            status=WorkItemStatus.QUEUED,
            node_id="node_123",
        )

    @pytest.mark.asyncio
    async def test_update_status_without_comment(
        self, sample_work_item: WorkItem
    ) -> None:
        """Test update_status without comment doesn't post comment."""
        queue = GitHubQueue(token="test-token")

        mock_delete_response = MagicMock()
        mock_delete_response.status_code = 200

        mock_post_response = MagicMock()
        mock_post_response.status_code = 200

        with (
            patch.object(
                queue._client, "delete", new_callable=AsyncMock
            ) as mock_delete,
            patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post,
        ):
            mock_delete.return_value = mock_delete_response
            mock_post.return_value = mock_post_response

            await queue.update_status(sample_work_item, WorkItemStatus.SUCCESS)

            # Should only be called once for labels, not for comment
            assert mock_post.call_count == 1

    @pytest.mark.asyncio
    async def test_update_status_with_comment(self, sample_work_item: WorkItem) -> None:
        """Test update_status with comment posts comment."""
        queue = GitHubQueue(token="test-token")

        mock_delete_response = MagicMock()
        mock_delete_response.status_code = 200

        mock_post_response = MagicMock()
        mock_post_response.status_code = 201

        with (
            patch.object(
                queue._client, "delete", new_callable=AsyncMock
            ) as mock_delete,
            patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post,
        ):
            mock_delete.return_value = mock_delete_response
            mock_post.return_value = mock_post_response

            await queue.update_status(
                sample_work_item, WorkItemStatus.SUCCESS, comment="Done!"
            )

            # Should be called twice: once for labels, once for comment
            assert mock_post.call_count == 2

            # Check the comment call
            comment_call = mock_post.call_args_list[1]
            assert "comments" in comment_call[0][0]
            assert comment_call[1]["json"]["body"] == "Done!"

    @pytest.mark.asyncio
    async def test_update_status_scrubs_secrets_in_comment(
        self, sample_work_item: WorkItem
    ) -> None:
        """Test update_status scrubs secrets from comment."""
        queue = GitHubQueue(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 200

        with (
            patch.object(
                queue._client, "delete", new_callable=AsyncMock
            ) as mock_delete,
            patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post,
        ):
            mock_delete.return_value = mock_response
            mock_post.return_value = mock_response

            await queue.update_status(
                sample_work_item,
                WorkItemStatus.SUCCESS,
                comment="Token: Bearer FAKE-TOKEN-FOR-TESTING-123==",
            )

            # Check the comment was scrubbed
            comment_call = mock_post.call_args_list[1]
            body = comment_call[1]["json"]["body"]
            assert "***REDACTED***" in body
            assert "FAKE-TOKEN" not in body

    @pytest.mark.asyncio
    async def test_update_status_deletes_in_progress_label(
        self, sample_work_item: WorkItem
    ) -> None:
        """Test update_status deletes in-progress label."""
        queue = GitHubQueue(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 200

        with (
            patch.object(
                queue._client, "delete", new_callable=AsyncMock
            ) as mock_delete,
            patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post,
        ):
            mock_delete.return_value = mock_response
            mock_post.return_value = mock_response

            await queue.update_status(sample_work_item, WorkItemStatus.SUCCESS)

            # Check delete was called with in-progress label
            delete_url = mock_delete.call_args[0][0]
            assert "agent:in-progress" in delete_url


class TestGitHubQueueClaimTask:
    """Tests for GitHubQueue.claim_task method."""

    @pytest.fixture
    def sample_work_item(self) -> WorkItem:
        """Provide a sample WorkItem for testing."""
        return WorkItem(
            id="123",
            issue_number=42,
            source_url="https://github.com/owner/repo/issues/42",
            context_body="Test task",
            target_repo_slug="owner/repo",
            task_type=TaskType.IMPLEMENT,
            status=WorkItemStatus.QUEUED,
            node_id="node_123",
        )

    @pytest.mark.asyncio
    async def test_claim_task_without_bot_login(
        self, sample_work_item: WorkItem
    ) -> None:
        """Test claim_task without bot_login skips assignment."""
        queue = GitHubQueue(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 200

        with (
            patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post,
            patch.object(
                queue._client, "delete", new_callable=AsyncMock
            ) as mock_delete,
        ):
            mock_post.return_value = mock_response
            mock_delete.return_value = mock_response

            result = await queue.claim_task(
                sample_work_item, sentinel_id="sentinel-1", bot_login=""
            )

            assert result is True
            # Should not call assignees endpoint
            for call in mock_post.call_args_list:
                assert "assignees" not in call[0][0]

    @pytest.mark.asyncio
    async def test_claim_task_with_bot_login_success(
        self, sample_work_item: WorkItem
    ) -> None:
        """Test successful claim with bot assignment."""
        queue = GitHubQueue(token="test-token")

        mock_assign_response = MagicMock()
        mock_assign_response.status_code = 201

        mock_verify_response = MagicMock()
        mock_verify_response.status_code = 200
        mock_verify_response.json.return_value = {"assignees": [{"login": "mybot"}]}

        mock_label_response = MagicMock()
        mock_label_response.status_code = 200

        with (
            patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post,
            patch.object(queue._client, "get", new_callable=AsyncMock) as mock_get,
            patch.object(
                queue._client, "delete", new_callable=AsyncMock
            ) as mock_delete,
        ):
            mock_post.return_value = mock_assign_response
            mock_get.return_value = mock_verify_response
            mock_delete.return_value = mock_label_response

            result = await queue.claim_task(
                sample_work_item,
                sentinel_id="sentinel-1",
                bot_login="mybot",
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_claim_task_assignment_fails(
        self, sample_work_item: WorkItem
    ) -> None:
        """Test claim_task returns False when assignment fails."""
        queue = GitHubQueue(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 422  # Unprocessable Entity

        with patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await queue.claim_task(
                sample_work_item,
                sentinel_id="sentinel-1",
                bot_login="mybot",
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_claim_task_loses_race(self, sample_work_item: WorkItem) -> None:
        """Test claim_task returns False when another bot wins the race."""
        queue = GitHubQueue(token="test-token")

        mock_assign_response = MagicMock()
        mock_assign_response.status_code = 201

        mock_verify_response = MagicMock()
        mock_verify_response.status_code = 200
        # Another bot is assigned
        mock_verify_response.json.return_value = {"assignees": [{"login": "otherbot"}]}

        with (
            patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post,
            patch.object(queue._client, "get", new_callable=AsyncMock) as mock_get,
        ):
            mock_post.return_value = mock_assign_response
            mock_get.return_value = mock_verify_response

            result = await queue.claim_task(
                sample_work_item,
                sentinel_id="sentinel-1",
                bot_login="mybot",
            )

            assert result is False


class TestGitHubQueuePostHeartbeat:
    """Tests for GitHubQueue.post_heartbeat method."""

    @pytest.fixture
    def sample_work_item(self) -> WorkItem:
        """Provide a sample WorkItem for testing."""
        return WorkItem(
            id="123",
            issue_number=42,
            source_url="https://github.com/owner/repo/issues/42",
            context_body="Test task",
            target_repo_slug="owner/repo",
            task_type=TaskType.IMPLEMENT,
            status=WorkItemStatus.IN_PROGRESS,
            node_id="node_123",
        )

    @pytest.mark.asyncio
    async def test_post_heartbeat_success(self, sample_work_item: WorkItem) -> None:
        """Test successful heartbeat post."""
        queue = GitHubQueue(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 201

        with patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            await queue.post_heartbeat(
                sample_work_item, sentinel_id="sentinel-1", elapsed_secs=300
            )

            assert mock_post.called
            call_url = mock_post.call_args[0][0]
            assert "comments" in call_url

            call_body = mock_post.call_args[1]["json"]["body"]
            assert "Heartbeat" in call_body
            assert "5m" in call_body  # 300 secs = 5 minutes

    @pytest.mark.asyncio
    async def test_post_heartbeat_handles_exception(
        self, sample_work_item: WorkItem
    ) -> None:
        """Test post_heartbeat handles exceptions gracefully."""
        queue = GitHubQueue(token="test-token")

        with patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Network error")

            # Should not raise
            await queue.post_heartbeat(
                sample_work_item, sentinel_id="sentinel-1", elapsed_secs=60
            )

    @pytest.mark.asyncio
    async def test_post_heartbeat_includes_sentinel_id(
        self, sample_work_item: WorkItem
    ) -> None:
        """Test heartbeat includes sentinel ID in message."""
        queue = GitHubQueue(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 201

        with patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            await queue.post_heartbeat(
                sample_work_item, sentinel_id="my-sentinel-123", elapsed_secs=120
            )

            call_body = mock_post.call_args[1]["json"]["body"]
            assert "my-sentinel-123" in call_body
