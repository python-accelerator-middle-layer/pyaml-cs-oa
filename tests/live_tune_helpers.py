import os
from pathlib import Path

import numpy as np
import pytest

TESTS_DIR = Path(__file__).parent

integration_marks = [
    pytest.mark.integration,
    pytest.mark.requires_control_system,
    pytest.mark.skipif(
        os.getenv("PYAML_CS_OA_RUN_INTEGRATION") != "1",
        reason="set PYAML_CS_OA_RUN_INTEGRATION=1 to run live tune tests",
    ),
]


def assert_tune_pair(value) -> np.ndarray:
    """Validate that a live tune readback has [horizontal, vertical] shape."""
    tune = np.asarray(value, dtype=float)
    assert tune.shape == (2,)
    return tune


def wait_seconds(default: float) -> float:
    return float(os.getenv("PYAML_CS_OA_TUNE_WAIT_SECONDS", str(default)))
