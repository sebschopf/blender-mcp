"""Abstract dispatcher interface for BlenderMCP.

Small ABC that captures the minimal dispatcher contract so concrete
implementations (legacy shims, new classes) can conform to a single
dependency-injectable contract.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

Handler = Callable[[Dict[str, Any]], Any]


class AbstractDispatcher(ABC):
    """Minimal dispatcher contract.

    Implementations must provide `register`, `unregister`, `list_handlers`
    and `dispatch` with the signatures below. This keeps the surface area
    small and enables dependency inversion for higher-level services.
    """

    @abstractmethod
    def register(self, name: str, fn: Handler, *, overwrite: bool = False) -> None:
        ...

    @abstractmethod
    def unregister(self, name: str) -> None:
        ...

    @abstractmethod
    def list_handlers(self) -> List[str]:
        ...

    @abstractmethod
    def dispatch(self, name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        ...
