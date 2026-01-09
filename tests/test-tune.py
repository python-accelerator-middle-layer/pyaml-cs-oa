from pyaml.accelerator import Accelerator
from pyaml.magnet.magnet import Magnet
from pyaml.common.constants import ACTION_RESTORE

import numpy as np
import time

def tune_callback(step: int, action: int, m: Magnet, dtune: np.array):
    if action == ACTION_RESTORE:
        # On action restore, the delta tune is passed as argument
        print(f"Tune response: #{step} {m.get_name()} {dtune}")
    return True

sr = Accelerator.load("EBSTune-ophyd.yaml",use_fast_loader=False)

#sr.design.get_lattice().disable_6d()
#tune_adjust = sr.design.get_tune_tuning("TUNE")
#tune_adjust.response.measure(callback=tune_callback)
#tune_adjust.response.save_json("tunemat.json")

sr.live.get_tune_tuning("TUNE").response.load_json("tunemat.json")
print(sr.live.get_tune_tuning("TUNE").readback())
sr.live.get_tune_tuning("TUNE").set([0.17, 0.32])
time.sleep(10)
print(sr.live.get_tune_tuning("TUNE").readback())
