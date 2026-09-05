"""Configuration helpers for backend-provided catalogs."""

from abc import ABCMeta, abstractmethod

from pydantic import BaseModel


class Catalog(metaclass=ABCMeta):
    r"""
    Abstract class for backend catalog configuration objects.

    Notes
    -----
    Concrete catalogs live in each control-system package. They may expose
    backend-specific resolution APIs, but those APIs are not called by the
    PyAML core.
    """

    @abstractmethod
    def resolve(self, key: str) -> BaseModel:
        """Return the configuration model associated with ``key``.

        Parameters
        ----------
        key : str
            Catalog key to resolve.
        """
        pass
