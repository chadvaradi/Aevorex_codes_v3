# FinanceHub module package

# ---------------------------------------------------------------------------
# Compatibility Shim for third-party packages that still import `pkg_resources`
# (e.g. pandas_ta).  Python 3.13 may ship without the legacy setuptools
# implementation, causing ModuleNotFoundError *before* our backend.main shim
# runs.  We therefore install a bare-bones stub at package import-time so every
# sub-module (`modules.financehub.*`) automatically has it in sys.modules.
# ---------------------------------------------------------------------------
import sys, types

if "pkg_resources" not in sys.modules:  # pragma: no cover – define once
    stub = types.ModuleType("pkg_resources")

    def _noop(*_a, **_kw):  # type: ignore
        return None

    # Provide minimal surface expected by pandas_ta
    stub.get_distribution = _noop  # type: ignore[attr-defined]
    class _DistNotFound(Exception):
        """Placeholder for setuptools' pkg_resources.DistributionNotFound"""
        pass

    stub.DistributionNotFound = _DistNotFound  # type: ignore[attr-defined]

    sys.modules["pkg_resources"] = stub 