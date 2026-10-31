"""Analysis queue with concurrency limiting via asyncio.Semaphore."""

import asyncio
from typing import Any, Callable, Coroutine


class AnalysisQueue:
    def __init__(self, max_concurrent: int = 3):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._pending = 0

    @property
    def pending_count(self) -> int:
        return self._pending

    async def submit(self, coro_func: Callable[..., Coroutine], *args: Any) -> Any:
        self._pending += 1
        try:
            async with self._semaphore:
                self._pending -= 1
                return await coro_func(*args)
        except Exception:
            self._pending -= 1
            raise


analysis_queue = AnalysisQueue(max_concurrent=3)
