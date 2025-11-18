from pyaml.control.controlsystem import ControlSystem
from pydantic import BaseModel


class OphydAsyncCompatibleControlSystemConfig(BaseModel):
    name: str


class OphydAsyncCompatibleControlSystem(ControlSystem):
    """A generic control system using ophyd_async backend."""

    def __init__(self, cfg: OphydAsyncCompatibleControlSystemConfig):
        super().__init__()
        self._cfg = cfg

    def name(self) -> str:
        """
        Return the name of the control system.

        Returns
        -------
        str
            Name of the control system.
        """
        return self._cfg.name

    def init_cs(self):
        """
        Initialize the control system.

        This method is a placeholder and should be implemented as needed.
        """
        pass
