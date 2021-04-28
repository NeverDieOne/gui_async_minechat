import asyncio
from contextlib import asynccontextmanager
from enum import Enum


@asynccontextmanager
async def manage_status(
    status_queue: asyncio.Queue,
    connection_manager: Enum
) -> None:
    status_queue.put_nowait(connection_manager.INITIATED)

    try:
        status_queue.put_nowait(connection_manager.ESTABLISHED)
        yield
    finally:
        status_queue.put_nowait(connection_manager.CLOSED)
