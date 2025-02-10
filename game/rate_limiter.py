"""
Rate limiter for SpaceTraders API

Handles rate limiting for API requests with:
- Burst limit tracking
- Request queueing
- Backoff strategies
- Response parsing for rate limit headers
"""
import asyncio
import json
import time
from typing import Optional, Dict, Any, Callable, Awaitable, TypeVar
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type variable for generic return type
T = TypeVar('T')

class RateLimiter:
    """Manages API rate limiting with queue processing and backoff"""

    def __init__(self):
        """Initialize rate limiter with default SpaceTraders limits"""
        # API Limits
        self.burst_limit = 30
        self.rate_per_second = 2
        self.min_request_interval = 1 / self.rate_per_second
        self.remaining_requests = self.burst_limit
        
        # Timing and State
        self.last_request_time = 0
        self.reset_time: Optional[datetime] = None
        self.backoff_multiplier = 1.0
        
        # Queue Management
        self._request_queue = asyncio.Queue()
        self._queue_processor_task = None
        self._running = True
        
        # Rate Limit Response Data
        self.rate_limit_data: Dict[str, Any] = {}

    async def start_queue_processor(self):
        """Start the queue processor if not already running"""
        if self._queue_processor_task is None or self._queue_processor_task.done():
            try:
                loop = asyncio.get_running_loop()
                if not loop.is_closed():
                    self._queue_processor_task = loop.create_task(self._process_queue())
            except RuntimeError:
                logger.warning("No running event loop available for queue processor")

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
                except asyncio.CancelledError:
                    break

                # Calculate time to wait
                now = time.time()
                time_since_last = now - self.last_request_time
                wait_time = max(0, self.min_request_interval - time_since_last)

                if wait_time > 0:
                    try:
                        await asyncio.sleep(wait_time)
                    except asyncio.CancelledError:
                        break

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

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in queue processor: {e}")
                try:
                    await asyncio.sleep(1)  # Avoid tight loop on error
                except asyncio.CancelledError:
                    break

        logger.info("Queue processor stopping")

    async def queue_request(self, callback: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """Queue an API request with rate limiting"""
        if not self._running:
            raise RuntimeError("Rate limiter is not running")

        # Create future for result
        future = asyncio.Future()

        try:
            # Start queue processor if needed
            await self.start_queue_processor()

            # Add request to queue
            await self._request_queue.put((callback, args, kwargs, future))

            # Wait for result
            return await future
        except asyncio.CancelledError:
            if not future.done():
                future.cancel()
            raise

    async def execute_with_retry(
        self,
        callback: Callable[..., Awaitable[T]],
        task_name: str = "API request",
        max_retries: int = 3,
        *args,
        **kwargs
    ) -> T:
        """Execute an API request with retries and rate limiting"""
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
                    try:
                        await asyncio.sleep(retry_after)
                    except asyncio.CancelledError:
                        raise
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
                        try:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        except asyncio.CancelledError:
                            raise
                        attempt += 1
                        continue
                    else:
                        # For client errors (4xx except 429), don't retry
                        return response

            except asyncio.CancelledError:
                raise
            except Exception as e:
                last_error = e
                logger.error(
                    f"{task_name} error (attempt {attempt + 1}/{max_retries}): {e}"
                )
                try:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                except asyncio.CancelledError:
                    raise
                attempt += 1

        # If we get here, all retries failed
        if last_error:
            raise Exception(f"{task_name} failed after {max_retries} attempts") from last_error
        elif last_response:
            return last_response
        else:
            raise Exception(f"{task_name} failed after {max_retries} attempts with no response")

    async def handle_response(self, response: Any) -> Optional[float]:
        """Handle API response and extract rate limit info"""
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

    async def cleanup(self):
        """Clean up the rate limiter and stop queue processor"""
        self._running = False
        
        if self._queue_processor_task is not None:
            # Cancel the task
            self._queue_processor_task.cancel()
            
            try:
                # Wait for task to finish
                await self._queue_processor_task
            except (asyncio.CancelledError, Exception) as e:
                logger.debug(f"Queue processor task cancelled: {e}")
            finally:
                self._queue_processor_task = None

        # Clear the queue
        while not self._request_queue.empty():
            try:
                callback, args, kwargs, future = self._request_queue.get_nowait()
                if not future.done():
                    future.cancel()
            except asyncio.QueueEmpty:
                break

    def __del__(self):
        """Ensure cleanup runs when the object is destroyed"""
        if self._queue_processor_task is not None and not self._queue_processor_task.done():
            loop = asyncio.get_event_loop_policy().get_event_loop()
            if loop.is_running():
                loop.create_task(self.cleanup())