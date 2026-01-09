from pyaml.accelerator import Accelerator
from pyaml.magnet.magnet import Magnet
from pyaml.common.constants import ACTION_RESTORE

import numpy as np
import time


def tune_callback(step: int, action: int, m: Magnet, dtune: np.array):
    if action == ACTION_RESTORE:
        # On action restore, the measured delta tune is passed as argument
        print(f"Tune response: #{step} {m.get_name()} {dtune}")
    return True

sr = Accelerator.load("bessy2tune-KL.yaml")

#print(sr.live.get_magnets("QForTune").strengths.get())
#print(sr.design.get_magnets("QForTune").strengths.get())
#quit()

#sr.design.get_lattice().disable_6d()
#tune_adjust = sr.design.tune
#tune_adjust.response.measure(callback=tune_callback)
#tune_adjust.response.save_json("tunemat-bessy.json")

sr.live.tune.response.load_json("tunemat-bessy.json")
print(sr.live.tune.readback())
sr.live.tune.set([0.83, 0.84],iter=2,wait_time=3)
time.sleep(3)
print(sr.live.tune.readback())

