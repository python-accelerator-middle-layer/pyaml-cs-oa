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
from pyaml.control.signal import arun
from pyaml.control.signal.container import Readback, Setpoint

T = TypeVar("T")


def _looks_disconnected(exc: BaseException) -> bool:
    # Keep it generic: ophyd-async wraps cancellations in TimeoutError;
    # tango/epics transports often raise CancelledError or "NotConnected" types.
    return isinstance(exc, (asyncio.CancelledError, TimeoutError))


async def _recover_once(
    run: Callable[[], Awaitable[T]],
    reconnect: Callable[[], Awaitable[None]],
    rebuild: Callable[[], Awaitable[None]] | Callable[[], None] | None = None,
) -> T:
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
            if rebuild is not None:
                maybe_awaitable = rebuild()
                if inspect.isawaitable(maybe_awaitable):
                    await maybe_awaitable
                await reconnect()
                return await run()
            raise


class OAReadback(Readback):
    """A readback object."""

    def __init__(self, r_signal: SignalR[SignalDatatypeT]):
        super().__init__(r_signal)

    async def _run_get(self) -> SignalDatatypeT:
        await self._r_sig.connect()
        backend = self._r_sig._connector.backend
        return await backend.get_value()

    async def async_get(self) -> SignalDatatypeT:
        return await _recover_once(
            self._run_get,
            self._r_sig.connect,
            getattr(self._r_sig, "__rebuild__", None),
        )

    async def _run_read(self) -> SignalDatatypeT:
        await self._r_sig.connect()
        backend = self._r_sig._connector.backend
        return await backend.get_reading()

    async def async_read(self) -> SignalDatatypeT:
        return await _recover_once(
            self._run_read,
            self._r_sig.connect,
            getattr(self._r_sig, "__rebuild__", None),
        )


class OASetpoint(Setpoint):
    def __init__(
        self,
        w_signal: SignalW[SignalDatatypeT],
        r_signal: SignalR[SignalDatatypeT] | None = None,
    ):
        super().__init__(w_signal, r_signal=r_signal)

    async def _run_get(self) -> SignalDatatypeT:
        await self._w_sig.connect()
        backend = self._w_sig._connector.backend
        return await backend.get_setpoint()

    async def async_get(self) -> SignalDatatypeT:
        return await _recover_once(
            self._run_get,
            self._w_sig.connect,
            getattr(self._w_sig, "__rebuild__", None),
        )

    async def _run_read(self) -> SignalDatatypeT:
        await self._w_sig.connect()
        backend = self._w_sig._connector.backend
        return await backend.get_reading()

    async def async_read(self) -> SignalDatatypeT:
        return await _recover_once(
            self._run_read,
            self._w_sig.connect,
            getattr(self._w_sig, "__rebuild__", None),
        )

    async def _run_set(self, value):
        await self._w_sig.connect()
        status = self._w_sig.set(value)
        return status

    async def async_set(self, value):
        return await _recover_once(
            lambda: self._run_set(value),
            self._w_sig.connect,
            getattr(self._w_sig, "__rebuild__", None),
        )

    async def _reconnect_both(self) -> None:
        await asyncio.gather(self._w_sig.connect(), self._r_sig.connect())

    async def _rebuild_both(self) -> None:
        w_rebuild = getattr(self._w_sig, "__rebuild__", None)
        r_rebuild = getattr(self._r_sig, "__rebuild__", None)
        if w_rebuild is not None:
            w_rebuild()
        if r_rebuild is not None:
            r_rebuild()

    async def _run_set_and_wait(self, value) -> None:
        if not self._has_r_sig:
            raise RuntimeError(
                "Cannot use set_and_wait() without a matching readback signal."
            )
        await self._reconnect_both()
        await set_and_wait_for_other_value(self._w_sig, value, self._r_sig, value)

    async def async_set_and_wait(self, value) -> None:
        return await _recover_once(
            lambda: self._run_set_and_wait(value),
            self._reconnect_both,
            self._rebuild_both,
        )
