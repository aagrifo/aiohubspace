__all__ = ["HubspaceBridgeV1", "HubspaceError", "InvalidAuth", "InvalidResponse"]


from importlib.metadata import PackageNotFoundError, version

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "aiohubspace"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError


from .errors import HubspaceError, InvalidAuth, InvalidResponse
from .v1 import HubspaceBridgeV1
