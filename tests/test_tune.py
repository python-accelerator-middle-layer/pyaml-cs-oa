from __future__ import annotations

import time

from pyaml.accelerator import Accelerator

from tests.live_tune_helpers import TESTS_DIR, assert_tune_pair, integration_marks, wait_seconds

pytestmark = integration_marks


def test_esrf_tune_correction_live(monkeypatch) -> None:
    """Run the ESRF tune example against live EPICS/Tango infrastructure."""
    monkeypatch.chdir(TESTS_DIR)
    accelerator = Accelerator.load("EBSTune-ophyd.yaml", use_fast_loader=False)
    tune = accelerator.live.get_tune_tuning("TUNE")

    tune.response.load_json("tunemat.json")

    assert_tune_pair(tune.readback())
    tune.set([0.17, 0.32])
    time.sleep(wait_seconds(10.0))
    assert_tune_pair(tune.readback())
