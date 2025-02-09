"""
Rate limiter for SpaceTraders API
"""
import asyncio
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimiter:
    """Manages API rate limiting"""

    def __init__(self):
        """Initialize rate limiter"""
        self.burst_limit = 30
        self.rate_per_second = 2
        self.min_request_interval = 1 / self.rate_per_second
        self.remaining_requests = self.burst_limit
        self.last_request_time = 0
        self.reset_time: Optional[datetime] = None
        self.backoff_multiplier = 1.0
        self._request_queue = asyncio.Queue()
        self._queue_processor_task = None
        self._running = True

    async def start_queue_processor(self):
        """Start the queue processor if not already running"""
        if self._queue_processor_task is None:
            self._queue_processor_task = asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        """Process queued requests with rate limiting"""
        while self._running:
            try:
                # Get next request from queue with timeout
                try:
                    callback, args, kwargs, future = await asyncio.wait_for(
                        self._request_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Calculate time to wait
                now = time.time()
                time_since_last = now - self.last_request_time
                wait_time = max(0, self.min_request_interval - time_since_last)

                if wait_time > 0:
                    await asyncio.sleep(wait_time)

                # Execute request
                try:
                    result = await callback(*args, **kwargs)
                    if not future.cancelled():
                        future.set_result(result)
                except Exception as e:
                    if not future.cancelled():
                        future.set_exception(e)
                finally:
                    self._request_queue.task_done()
                    self.last_request_time = time.time()

            except Exception as e:
                logger.error(f"Error in queue processor: {e}")
                await asyncio.sleep(1)  # Avoid tight loop on error

        logger.info("Queue processor stopping")

    async def handle_response(self, response: Any) -> Optional[float]:
        """Handle API response and extract rate limit info

        Args:
            response: API response object

        Returns:
            Delay in seconds if rate limited, None otherwise
        """
        # Update rate limit info from headers if available
        # TODO: Add header parsing when API provides them

        if response.status_code == 429:
            try:
                error_data = json.loads(response.content.decode())
                rate_data = error_data.get('error', {}).get('data', {})

                # Update our limits
                self.burst_limit = rate_data.get('limitBurst', self.burst_limit)
                self.rate_per_second = rate_data.get('limitPerSecond', self.rate_per_second)
                self.remaining_requests = rate_data.get('remaining', 0)

                # Parse reset time
                reset_str = rate_data.get('reset')
                if reset_str:
                    self.reset_time = datetime.fromisoformat(reset_str.replace('Z', '+00:00'))

                # Get retry delay
                retry_after = rate_data.get('retryAfter', 1)

                # Apply backoff multiplier
                actual_delay = retry_after * self.backoff_multiplier
                self.backoff_multiplier = min(self.backoff_multiplier * 1.5, 5.0)  # Cap at 5x

                logger.info(
                    f"Rate limited. Waiting {actual_delay:.2f}s "
                    f"(backoff: {self.backoff_multiplier:.1f}x)"
                )

                return actual_delay

            except Exception as e:
                logger.error(f"Error parsing rate limit response: {e}")
                return 1.0  # Default 1 second delay
        else:
            # Successful request, reset backoff
            self.backoff_multiplier = 1.0
            return None

    async def queue_request(self, callback, *args, **kwargs):
        """Queue an API request with rate limiting

        Args:
            callback: Async function to call
            *args: Positional arguments for callback
            **kwargs: Keyword arguments for callback

        Returns:
            Result from callback
        """
        # Create future for result
        future = asyncio.Future()

        # Start queue processor if needed
        await self.start_queue_processor()

        # Add request to queue
        await self._request_queue.put((callback, args, kwargs, future))

        # Wait for result
        return await future

    async def execute_with_retry(
        self,
        callback,
        max_retries: int = 3,
        task_name: str = "API request",
        *args,
        **kwargs
    ):
        """Execute an API request with retries and rate limiting

        Args:
            callback: Async function to call
            max_retries: Maximum number of retry attempts
            task_name: Name of task for logging
            *args: Positional arguments for callback
            **kwargs: Keyword arguments for callback

        Returns:
            Result from callback

        Raises:
            Exception: If all retries fail
        """
        attempt = 0
        last_error = None
        last_response = None

        while attempt < max_retries:
            try:
                # Attempt request
                response = await self.queue_request(callback, *args, **kwargs)
                last_response = response

                # Check for rate limiting
                retry_after = await self.handle_response(response)
                if retry_after:
                    await asyncio.sleep(retry_after)
                    attempt += 1
                    continue

                # Check response status
                if response.status_code in [200, 201]:
                    return response
                else:
                    logger.warning(
                        f"{task_name} failed (attempt {attempt + 1}/{max_retries}): "
                        f"Status {response.status_code}"
                    )
                    if response.content:
                        try:
                            error_content = response.content.decode()
                            logger.warning(f"Response: {error_content}")
                        except Exception:
                            logger.warning("Could not decode error content")

                    # Only retry on server errors and rate limiting
                    if (500 <= response.status_code < 600) or response.status_code == 429:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        attempt += 1
                        continue
                    else:
                        # For client errors (4xx except 429), don't retry
                        return response

            except Exception as e:
                last_error = e
                logger.error(
                    f"{task_name} error (attempt {attempt + 1}/{max_retries}): {e}"
                )
                # Only retry on general exceptions and specific retryable errors
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                attempt += 1

        # If we get here, all retries failed
        if last_error:
            # Wrap the exception with our task context
            raise Exception(f"{task_name} failed after {max_retries} attempts") from last_error
        elif last_response:
            # If no exception but failed response, return it
            return last_response
        else:
            # Should rarely happen, but handle the case
            raise Exception(f"{task_name} failed after {max_retries} attempts with no response")

    async def cleanup(self):
        """Clean up the rate limiter and stop queue processor"""
        self._running = False
        if self._queue_processor_task is not None:
            try:
                # Wait for task to finish with timeout
                self._queue_processor_task.cancel()
                await asyncio.wait_for(self._queue_processor_task, timeout=2.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                logger.warning("Queue processor task cancelled or timed out during cleanup")
            finally:
                self._queue_processor_task = None
