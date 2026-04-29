from __future__ import annotations

import time

from pyaml.accelerator import Accelerator

from tests.live_tune_helpers import TESTS_DIR, assert_tune_pair, integration_marks
from tests.live_tune_helpers import wait_seconds

pytestmark = integration_marks


def test_bessy_tune_correction_live(monkeypatch) -> None:
    """Run the BESSY II tune example against the live virtual accelerator."""
    monkeypatch.chdir(TESTS_DIR)
    accelerator = Accelerator.load("bessy2tune-KL.yaml")
    tune = accelerator.live.tune

    tune.response.load_json("tunemat-bessy.json")

    assert_tune_pair(tune.readback())
    tune.set([0.83, 0.84], iter=2, wait_time=3)
    time.sleep(wait_seconds(3.0))
    assert_tune_pair(tune.readback())
