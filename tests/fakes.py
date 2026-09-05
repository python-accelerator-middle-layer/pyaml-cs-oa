from collections import deque
from types import SimpleNamespace
from typing import Any


class AwaitableStatus:
    """Small awaitable status object matching the part of ophyd status used here."""

    def __init__(self) -> None:
        self.awaited = False

    def __await__(self):
        async def _wait():
            self.awaited = True
            return None

        return _wait().__await__()


class FakeBackend:
    """Async backend fake used by OAReadback/OASetpoint tests."""

    def __init__(
        self,
        value: Any = None,
        setpoint: Any = None,
        reading: Any = None,
        value_side_effects: list[Any] | None = None,
    ) -> None:
        self.value = value
        self.setpoint = setpoint
        self.reading = reading
        self.value_calls = 0
        self.setpoint_calls = 0
        self.reading_calls = 0
        self._value_side_effects = deque(value_side_effects or [])

    async def get_value(self) -> Any:
        self.value_calls += 1
        if self._value_side_effects:
            next_value = self._value_side_effects.popleft()
            if isinstance(next_value, BaseException):
                raise next_value
            return next_value
        return self.value

    async def get_setpoint(self) -> Any:
        self.setpoint_calls += 1
        return self.setpoint

    async def get_reading(self) -> Any:
        self.reading_calls += 1
        return self.reading


class FakeSignal:
    """Minimal signal fake exposing the attributes used by container.py."""

    def __init__(self, backend: FakeBackend, name: str = "fake-signal") -> None:
        self.name = name
        self._connector = SimpleNamespace(backend=backend)
        self.connect_calls = 0
        self.set_calls: list[Any] = []
        self.statuses: list[AwaitableStatus] = []

    async def connect(self) -> None:
        self.connect_calls += 1

    def set(self, value: Any) -> AwaitableStatus:
        self.set_calls.append(value)
        status = AwaitableStatus()
        self.statuses.append(status)
        return status


class PeerRebuilder:
    """Callable peer used to assert that recovery asks an OASignal to rebuild."""

    def __init__(self) -> None:
        self.calls = 0

    def build(self) -> None:
        self.calls += 1
