from pyaml.common.exception import PyAMLException

from .signal import OASignal
from .types import ControlSysConfig


class FloatSignalContainer(OASignal):
    """
    Class that implements a PyAML Float/FloatArray Signal using ophyd_async Signals.
    """

    def __init__(self, cfg: ControlSysConfig):
        super().__init__(cfg)

    def _indexed_float(self, value) -> float:
        if self._cfg.index is None:
            try:
                return float(value)
            except (TypeError, ValueError) as exc:
                raise PyAMLException(f"{self.name()}: cannot be converted to float; got {type(value).__name__}.") from exc

        else:
            try:
                return value[self._cfg.index]
            except (IndexError, KeyError, TypeError) as exc:
                raise PyAMLException(
                    f"{self.name()}: cannot read index {self._cfg.index} from "
                    f"backend.get_value() result of type {type(value).__name__}."
                ) from exc

    def get(self):
        """
        Get the last written value(s) of the attribute.

        Returns
        -------
        float | list[float]
            The last written value(s).

        """
        if self._writable:
            return self._indexed_float(self.SP.get())
        else:
            return self._indexed_float(self.RB.get())

    def readback(self):
        """
        Return the readback value(s) with metadata.

        Returns
        -------
        Value | list[Value]
            The readback value(s) including quality and timestamp.

        """
        return self._indexed_float(self.RB.get())

    def set(self, value):
        """
        Write a value asynchronously to the device.

        Parameters
        ----------
        value : float | list[float]
            Value(s) to write to the attribute.

        """
        # TODO handle indexed write
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
