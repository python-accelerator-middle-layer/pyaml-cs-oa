from __future__ import annotations

import pytest

from pyaml_cs_oa import arun
from pyaml_cs_oa.container import OAReadback, OASetpoint

from tests.fakes import FakeBackend, FakeSignal, PeerRebuilder


def test_readback_get_returns_backend_value(fake_signal: FakeSignal) -> None:
    readback = OAReadback(fake_signal)

    assert readback.get() == 1.5
    assert fake_signal.connect_calls == 1


@pytest.mark.parametrize("method_name", ["async_get", "async_read"])
def test_readback_async_methods_connect_before_reading(
    method_name: str,
) -> None:
    backend = FakeBackend(value=3.0, reading={"value": 3.0})
    signal = FakeSignal(backend)
    readback = OAReadback(signal)

    result = arun(getattr(readback, method_name)())

    assert result in (3.0, {"value": 3.0})
    assert signal.connect_calls == 1


def test_setpoint_get_returns_backend_setpoint() -> None:
    signal = FakeSignal(FakeBackend(setpoint=4.25))
    setpoint = OASetpoint(signal)

    assert setpoint.get() == 4.25
    assert signal.connect_calls == 1


def test_setpoint_set_delegates_to_wrapped_signal() -> None:
    signal = FakeSignal(FakeBackend())
    setpoint = OASetpoint(signal)

    status = setpoint.set(7.0)

    assert signal.set_calls == [7.0]
    assert status is signal.statuses[0]
    assert status.awaited is True


def test_set_and_wait_without_readback_raises_clear_error() -> None:
    setpoint = OASetpoint(FakeSignal(FakeBackend()))

    with pytest.raises(RuntimeError, match="without a matching readback signal"):
        setpoint.set_and_wait(1.0)


def test_readback_recovers_once_after_disconnect_like_failure() -> None:
    backend = FakeBackend(value_side_effects=[TimeoutError(), 8.5])
    signal = FakeSignal(backend)
    readback = OAReadback(signal)

    assert readback.get() == 8.5
    assert backend.value_calls == 2
    assert signal.connect_calls == 3


def test_readback_rebuilds_peer_when_reconnect_retry_fails() -> None:
    backend = FakeBackend(value_side_effects=[TimeoutError(), TimeoutError(), 9.5])
    signal = FakeSignal(backend)
    peer = PeerRebuilder()
    signal.__peer__ = peer
    readback = OAReadback(signal)

    assert readback.get() == 9.5
    assert peer.calls == 1
    assert backend.value_calls == 3
