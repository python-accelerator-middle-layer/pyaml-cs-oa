from .signal import OASignal
from .types import ControlSysConfig
from pyaml.common.exception import PyAMLException

class FloatSignalContainer(OASignal):
    """
    Class that implements a PyAML Float/FloatArray Signal using ophyd_async Signals.
    """

    def __init__(self, cfg: ControlSysConfig,is_array:bool):
        super().__init__(cfg,is_array)

    def _indexed_float(self,signal_name: str, value, index: int) -> float:

        if self._cfg.index is None:
            try:
                return float(indexed_value)    
            except (TypeError, ValueError) as exc:
                raise PyAMLException(
                    f"{signal_name}: backend.get_value()[{index}] cannot be converted "
                    f"to float; got {type(indexed_value).__name__}."
                ) from exc
        

        try:
            indexed_value = value[index]
        except (IndexError, KeyError, TypeError) as exc:
            raise PyAMLException(
                f"{signal_name}: cannot read index {index} from "
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
