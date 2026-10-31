"""WebSocket endpoint for analysis progress tracking."""

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Simple in-memory progress store (job_id -> status)
progress_store: dict[str, str] = {}


def update_progress(job_id: str, status: str) -> None:
    progress_store[job_id] = status


@router.websocket("/ws/analysis/{job_id}")
async def analysis_progress(websocket: WebSocket, job_id: str) -> None:
    await websocket.accept()
    try:
        last_status = None
        while True:
            status = progress_store.get(job_id, "queued")
            if status != last_status:
                await websocket.send_json({"status": status})
                last_status = status
            if status in ("done", "error"):
                break
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass
    finally:
        # Cleanup old entries
        progress_store.pop(job_id, None)
