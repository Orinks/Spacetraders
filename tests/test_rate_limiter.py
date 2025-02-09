"""Tests for rate limiter functionality"""
import json
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone
import asyncio

from game.rate_limiter import RateLimiter

# Mock response data
MOCK_RATE_LIMIT_RESPONSE = {
    "error": {
        "message": "Rate limit exceeded",
        "code": 429,
        "data": {
            "limitBurst": 10,
            "limitPerSecond": 2,
            "remaining": 0,
            "reset": "2024-01-01T00:00:00Z",
            "retryAfter": 1.5
        }
    }
}


@pytest.fixture
async def rate_limiter():
    """Fixture for RateLimiter instance"""
    limiter = RateLimiter()
    yield limiter
    await limiter.cleanup()


@pytest.fixture
def mock_429_response():
    """Fixture for rate limit response"""
    response = MagicMock()
    response.status_code = 429
    response.content = json.dumps(MOCK_RATE_LIMIT_RESPONSE).encode()
    return response


@pytest.fixture
def mock_200_response():
    """Fixture for successful response"""
    response = MagicMock()
    response.status_code = 200
    return response


class TestRateLimiter:
    """Test suite for RateLimiter class"""

    def test_init(self, rate_limiter):
        """Test initialization"""
        assert rate_limiter.burst_limit == 30
        assert rate_limiter.rate_per_second == 2
        assert rate_limiter.min_request_interval == 0.5
        assert rate_limiter.remaining_requests == 30
        assert rate_limiter.backoff_multiplier == 1.0

    @pytest.mark.asyncio
    async def test_handle_response_success(self, rate_limiter, mock_200_response):
        """Test handling successful response"""
        retry_after = await rate_limiter.handle_response(mock_200_response)
        assert retry_after is None
        assert rate_limiter.backoff_multiplier == 1.0

    @pytest.mark.asyncio
    async def test_handle_response_rate_limit(self, rate_limiter, mock_429_response):
        """Test handling rate limit response"""
        retry_after = await rate_limiter.handle_response(mock_429_response)
        
        assert retry_after == 1.5  # Initial retry with no backoff
        assert rate_limiter.burst_limit == 10  # Updated from response
        assert rate_limiter.rate_per_second == 2
        assert rate_limiter.remaining_requests == 0
        assert rate_limiter.backoff_multiplier == 1.5  # Increased after rate limit

    @pytest.mark.asyncio
    async def test_backoff_multiplier_increase(self, rate_limiter, mock_429_response):
        """Test backoff multiplier increases with consecutive rate limits"""
        initial_multiplier = rate_limiter.backoff_multiplier
        
        # First rate limit
        await rate_limiter.handle_response(mock_429_response)
        first_multiplier = rate_limiter.backoff_multiplier
        assert first_multiplier > initial_multiplier
        
        # Second rate limit
        await rate_limiter.handle_response(mock_429_response)
        second_multiplier = rate_limiter.backoff_multiplier
        assert second_multiplier > first_multiplier
        
        # Verify multiplier is capped
        for _ in range(5):
            await rate_limiter.handle_response(mock_429_response)
        assert rate_limiter.backoff_multiplier <= 5.0

    @pytest.mark.asyncio
    async def test_queue_request(self, rate_limiter):
        """Test request queuing"""
        async def mock_api_call(*args, **kwargs):
            return MagicMock(status_code=200)

        # Queue multiple requests
        results = await asyncio.gather(
            rate_limiter.queue_request(mock_api_call),
            rate_limiter.queue_request(mock_api_call),
            rate_limiter.queue_request(mock_api_call)
        )
        
        assert len(results) == 3
        for result in results:
            assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_execute_with_retry_success(self, rate_limiter, mock_200_response):
        """Test successful execution with retry logic"""
        async def mock_success(*args, **kwargs):
            return mock_200_response

        result = await rate_limiter.execute_with_retry(
            mock_success,
            task_name="test_task"
        )
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_execute_with_retry_fails_after_max_retries(self, rate_limiter):
        """Test retry exhaustion"""
        async def mock_failure(*args, **kwargs):
            raise Exception("API Error")

        with pytest.raises(Exception, match="test_task failed after 3 attempts"):
            await rate_limiter.execute_with_retry(
                mock_failure,
                task_name="test_task"
            )

    @pytest.mark.asyncio
    async def test_execute_with_retry_rate_limit_recovery(
        self,
        rate_limiter,
        mock_429_response,
        mock_200_response
    ):
        """Test recovery after rate limit"""
        response_sequence = [mock_429_response, mock_200_response]
        call_count = 0
        
        async def mock_api_call(*args, **kwargs):
            nonlocal call_count
            response = response_sequence[min(call_count, len(response_sequence) - 1)]
            call_count += 1
            return response

        result = await rate_limiter.execute_with_retry(
            mock_api_call,
            task_name="test_task"
        )
        assert result.status_code == 200
        assert call_count == 2  # One rate limit + one success