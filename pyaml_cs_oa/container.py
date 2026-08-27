"""Synchronous and reconnecting adapters around ophyd-async signals."""

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from typing import TypeVar

from ophyd_async.core import (
    SignalDatatypeT,
    SignalR,
    SignalW,
    set_and_wait_for_other_value,
)

from . import arun
from .signal import OASignal

T = TypeVar("T")


def _looks_disconnected(exc: BaseException) -> bool:
    """Return whether an exception plausibly indicates a lost connection."""
    # Keep it generic: ophyd-async wraps cancellations in TimeoutError;
    # tango/epics transports often raise CancelledError or "NotConnected" types.
    return isinstance(exc, (asyncio.CancelledError, TimeoutError))


async def _recover_once(
    run: Callable[[], Awaitable[T]],
    reconnect: Callable[[], Awaitable[None]],
    peer,
) -> T:
    """Run an operation, reconnecting and rebuilding its signal once if needed."""
    try:
        return await run()
    except BaseException as exc:
        if not _looks_disconnected(exc):
            raise
        # Attempt reconnect of the same Signal first
        try:
            await reconnect()
            return await run()
        except BaseException:
            # If that fails and we have a way to rebuild, do so and try one more time
            if peer is not None:
                maybe_awaitable = peer.build()
                if inspect.isawaitable(maybe_awaitable):
                    await maybe_awaitable
                await reconnect()
                return await run()
            raise


class OAReadback:
    """Adapter exposing asynchronous and synchronous readback operations."""

    def __init__(self, r_signal: SignalR[SignalDatatypeT]):
        self._r_sig = r_signal

    async def _run_get(self) -> SignalDatatypeT:
        """Connect and fetch the backend's current value."""
        await self._r_sig.connect()
        backend = self._r_sig._connector.backend
        print(f"Read {self._r_sig.name}")
        return await backend.get_value()

    async def async_get(self) -> SignalDatatypeT:
        """Fetch the current value, retrying once after reconnect."""
        return await _recover_once(
            self._run_get,
            self._r_sig.connect,
            getattr(self._r_sig, "__peer__", None),
        )

    async def _run_read(self) -> SignalDatatypeT:
        """Connect and fetch the backend reading."""
        await self._r_sig.connect()
        backend = self._r_sig._connector.backend
        return await backend.get_reading()

    async def async_read(self) -> SignalDatatypeT:
        """Fetch a reading, retrying once after reconnect."""
        return await _recover_once(
            self._run_read,
            self._r_sig.connect,
            getattr(self._r_sig, "__peer__", None),
        )

    def get(self) -> SignalDatatypeT:
        """Synchronous wrapper around `async_get()`."""
        return arun(self.async_get())


class OASetpoint:
    """Adapter exposing setpoint read, write, and wait operations."""

    def __init__(
        self,
        w_signal: SignalW[SignalDatatypeT],
        r_signal: SignalR[SignalDatatypeT] | None = None,
    ):
        self._w_sig = w_signal
        self._r_sig = r_signal  # used only for `set_and_wait()`
        self._has_r_sig = r_signal is not None

    async def _run_get(self) -> SignalDatatypeT:
        """Connect and fetch the current setpoint."""
        await self._w_sig.connect()
        backend = self._w_sig._connector.backend
        return await backend.get_setpoint()

    async def async_get(self) -> SignalDatatypeT:
        """Fetch the setpoint, retrying once after reconnect."""
        return await _recover_once(
            self._run_get,
            self._w_sig.connect,
            getattr(self._w_sig, "__peer__", None),
        )

    async def _run_read(self) -> SignalDatatypeT:
        """Connect and fetch the setpoint signal's reading."""
        await self._w_sig.connect()
        backend = self._w_sig._connector.backend
        return await backend.get_reading()

    async def async_read(self) -> SignalDatatypeT:
        """Fetch a setpoint reading, retrying once after reconnect."""
        return await _recover_once(
            self._run_read,
            self._w_sig.connect,
            getattr(self._w_sig, "__peer__", None),
        )

    async def _run_set(self, value):
        """Connect and submit a value to the backend."""
        await self._w_sig.connect()
        status = self._w_sig.set(value)
        return status

    async def async_set(self, value):
        """Submit a value, retrying once after reconnect."""
        return await _recover_once(
            lambda: self._run_set(value),
            self._w_sig.connect,
            getattr(self._w_sig, "__peer__", None),
        )

    async def _reconnect_both(self) -> None:
        """Reconnect the write signal and optional readback signal."""
        if self._r_sig:
            await asyncio.gather(self._w_sig.connect(), self._r_sig.connect())

    async def _rebuild_both(self) -> None:
        """Rebuild peer signals after a failed reconnect."""
        w_rebuild = getattr(self._w_sig, "__peer__", None)
        r_rebuild = getattr(self._r_sig, "__peer__", None)
        if w_rebuild is not None:
            w_rebuild()
        if r_rebuild is not None:
            r_rebuild()

    async def _run_set_and_wait(self, value) -> None:
        """Set a value and wait until the readback reports it."""
        if not self._has_r_sig:
            raise RuntimeError("Cannot use set_and_wait() without a matching readback signal.")
        await self._reconnect_both()
        await set_and_wait_for_other_value(self._w_sig, value, self._r_sig, value)

    async def async_set_and_wait(self, value) -> None:
        """Set and await a matching readback value, with recovery."""
        return await _recover_once(
            lambda: self._run_set_and_wait(value),
            self._reconnect_both,
            self._rebuild_both,
        )

    async def _complete_set(self, value):
        """Submit a value and await its completion status."""
        status = await self.async_set(value)
        await status  # Wait for completion before returning
        return status

    def set(self, value):
        """Synchronous wrapper around `async_set()`."""
        return arun(self._complete_set(value))

    def get(self) -> SignalDatatypeT:
        """Synchronous wrapper around `async_get()`."""
        return arun(self.async_get())

    def set_and_wait(self, value) -> None:
        """Synchronous wrapper around `async_set_and_wait()`."""
        return arun(self.async_set_and_wait(value))
