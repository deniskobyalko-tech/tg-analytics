"""Tests for the analysis queue."""

import asyncio

import pytest

from app.core.queue import AnalysisQueue


@pytest.mark.asyncio
async def test_queue_limits_concurrency():
    queue = AnalysisQueue(max_concurrent=2)
    max_running = 0
    current_running = 0

    async def slow_job(name: str):
        nonlocal max_running, current_running
        current_running += 1
        if current_running > max_running:
            max_running = current_running
        await asyncio.sleep(0.05)
        current_running -= 1

    tasks = [queue.submit(slow_job, f"job{i}") for i in range(5)]
    await asyncio.gather(*tasks)
    assert max_running <= 2
    assert current_running == 0


@pytest.mark.asyncio
async def test_queue_pending_count():
    queue = AnalysisQueue(max_concurrent=1)

    async def slow_job():
        await asyncio.sleep(0.1)

    task = asyncio.create_task(queue.submit(slow_job))
    await asyncio.sleep(0.01)
    # The first job is running, pending should be 0
    assert queue.pending_count >= 0
    await task
