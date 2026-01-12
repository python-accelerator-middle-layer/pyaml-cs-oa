from .signal import OASignal
from .types import ControlSysConfig

class FloatSignalContainer(OASignal):
    """
    Class that implements a PyAML Float Signal using ophyd_async Signals.
    """

    def __init__(self, cfg: ControlSysConfig):
        super().__init__(cfg)

    def get(self) -> float:
        """
        Get the last written value of the attribute.

        Returns
        -------
        float
            The last written value.

        """
        if self._writable:
            return self.SP.get()
        else:
            return self.RB.get()

    def readback(self) -> float:
        """
        Return the readback value with metadata.

        Returns
        -------
        Value
            The readback value including quality and timestamp.

        """
        return self.RB.get()

    def set(self, value: float):
        """
        Write a value asynchronously to the Tango attribute.

        Parameters
        ----------
        value : float
            Value to write to the attribute.

        """
        return self.SP.set(value)

    def set_and_wait(self, value: float):
        """
        Write a value synchronously to the Tango attribute.

        Parameters
        ----------
        value : float
            Value to write to the attribute.

        """
        self.SP.set_and_wait(value)
