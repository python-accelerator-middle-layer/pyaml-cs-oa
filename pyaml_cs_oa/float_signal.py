from .signal import OASignal
from .types import ControlSysConfig

class FloatSignalContainer(OASignal):
    """
    Class that implements a PyAML Float/FloatArray Signal using ophyd_async Signals.
    """

    def __init__(self, cfg: ControlSysConfig,is_array:bool):
        super().__init__(cfg,is_array)

    def get(self):
        """
        Get the last written value(s) of the attribute.

        Returns
        -------
        float | list[float]
            The last written value(s).

        """
        if self._writable:
            return self.SP.get()
        else:
            return self.RB.get()

    def readback(self):
        """
        Return the readback value(s) with metadata.

        Returns
        -------
        Value | list[Value]
            The readback value(s) including quality and timestamp.

        """
        return self.RB.get()

    def set(self, value):
        """
        Write a value asynchronously to the device.

        Parameters
        ----------
        value : float | list[float]
            Value(s) to write to the attribute.

        """
        return self.SP.set(value)

    def set_and_wait(self, value):
        """
        Write a value(s) synchronously to the device.

        Parameters
        ----------
        value : float | list[float]
            Value to write to the attribute.

        """
        self.SP.set_and_wait(value)
