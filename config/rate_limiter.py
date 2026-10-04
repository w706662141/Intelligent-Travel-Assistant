import asyncio
import time


class RateLimiter:

    def __init__(self, interval: float = 0.4):
        self.interval = interval
        self._lock = asyncio.Lock()
        self._last_request_time = 0.0

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()

            wait_time = (
                self.interval
                - (now - self._last_request_time)
            )

            if wait_time > 0:
                await asyncio.sleep(wait_time)

            self._last_request_time = time.monotonic()