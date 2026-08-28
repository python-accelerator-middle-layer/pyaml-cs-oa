"""Shared asyncio utilities for the ophyd-async pyAML control-system plugin."""

import asyncio
import contextlib
from typing import Any, Awaitable

# One persistent event loop
_loop = None
_nest_asyncio_applied = False


def loop() -> asyncio.AbstractEventLoop:
    """Return the persistent event loop used by synchronous wrappers.

    Returns
    -------
    asyncio.AbstractEventLoop
        The currently running loop, or the package-managed loop.
    """
    global _loop, _nest_asyncio_applied

    # Try to get the currently running loop (e.g., in Jupyter)
    try:
        running_loop = asyncio.get_running_loop()
        # We found a running loop (Jupyter case)
        if not _nest_asyncio_applied:
            try:
                import nest_asyncio

                nest_asyncio.apply(running_loop)
                _nest_asyncio_applied = True
            except ImportError:
                pass
        return running_loop
    except RuntimeError:
        # No running loop, create our own
        pass

    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)

        # Apply nest_asyncio to our new loop
        if not _nest_asyncio_applied:
            try:
                import nest_asyncio

                nest_asyncio.apply(_loop)
                _nest_asyncio_applied = True
            except ImportError:
                pass

    return _loop


loop()  # Make sure to initialize `_loop`


def _reap_done_tasks(evloop: asyncio.AbstractEventLoop) -> None:
    """Reap exceptions from tasks that are already DONE on this loop.
    Does not cancel or otherwise touch pending tasks.
    """
    if evloop is None or evloop.is_closed():
        return

    try:
        # Snapshot; tasks may change during iteration
        for t in tuple(asyncio.all_tasks(evloop)):
            if not t.done():
                continue
            # If the task is cancelled, .result() raises CancelledError — suppress that.
            # If the task failed, .result() raises its exception — suppress to just mark it retrieved.
            with contextlib.suppress(asyncio.CancelledError, Exception):
                t.result()
    except (RuntimeError, AttributeError):
        # During shutdown, asyncio may be partially cleaned up
        pass


def arun(coro: Awaitable[Any]) -> Any:
    """Run an awaitable to completion on the package event loop.

    Parameters
    ----------
    coro : Awaitable[Any]
        Awaitable to execute.

    Returns
    -------
    Any
        The awaitable's result.
    """
    evloop = loop()

    try:
        return evloop.run_until_complete(coro)
    finally:
        # Clean up completed/cancelled tasks so residual CancelledError
        # doesn't leak to next run
        _reap_done_tasks(evloop)
