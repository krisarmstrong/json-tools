"""json-tools public package surface."""

from . import converters, json_ops

try:  # pragma: no cover - version injected at build time
    from ._version import version as __version__
except ImportError:  # pragma: no cover - fallback for editable installs before scm runs
    __version__ = "2.0.4"

__all__ = ["__version__", "converters", "json_ops"]
