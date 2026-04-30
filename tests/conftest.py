import pytest

from tests.fakes import FakeBackend, FakeSignal


@pytest.fixture
def fake_backend() -> FakeBackend:
    return FakeBackend(value=1.5, setpoint=2.5, reading={"value": 1.5})


@pytest.fixture
def fake_signal(fake_backend: FakeBackend) -> FakeSignal:
    return FakeSignal(fake_backend)
