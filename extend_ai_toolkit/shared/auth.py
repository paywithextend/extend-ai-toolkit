from __future__ import annotations

import inspect
from typing import Dict, Optional, Protocol

from extend import ExtendClient

try:  # pragma: no cover - module availability depends on paywithextend version
    from extend.auth import Authorization as _ExtendAuthorization  # type: ignore
    from extend.auth import BasicAuth as _ExtendBasicAuth  # type: ignore
except ImportError:  # pragma: no cover - legacy paywithextend versions
    _ExtendAuthorization = None
    _ExtendBasicAuth = None


class Authorization(Protocol):
    """Protocol describing the paywithextend authorization interface."""

    def get_auth_headers(self) -> Dict[str, str]:  # pragma: no cover - protocol method
        ...


def supports_authorization() -> bool:
    """Return True when the installed paywithextend package supports auth objects."""

    return (
        _ExtendAuthorization is not None
        and "auth" in inspect.signature(ExtendClient.__init__).parameters
    )


def build_basic_auth(api_key: str, api_secret: str):
    """Create a BasicAuth instance when available, raising if unsupported."""

    if _ExtendBasicAuth is None:
        raise RuntimeError(
            "extend.auth.BasicAuth is unavailable; install paywithextend>=2.0.0 to "
            "use authorization objects."
        )
    return _ExtendBasicAuth(api_key, api_secret)


def create_extend_client(
    api_key: str,
    api_secret: str,
    auth: Optional[Authorization] = None,
) -> ExtendClient:
    """Instantiate ExtendClient supporting both legacy and auth-based signatures."""

    if supports_authorization():
        if auth is None:
            auth = build_basic_auth(api_key, api_secret)
        return ExtendClient(auth=auth)

    if auth is not None:
        raise ValueError(
            "Custom Authorization requires paywithextend>=2.0.0; current version "
            "accepts only api_key/api_secret parameters."
        )

    return ExtendClient(api_key=api_key, api_secret=api_secret)


def create_client_with_auth(auth: Authorization) -> ExtendClient:
    """Instantiate ExtendClient strictly with an authorization object."""

    if not supports_authorization():
        raise ValueError(
            "Authorization objects require paywithextend>=2.0.0; upgrade the "
            "dependency to use this capability."
        )
    return ExtendClient(auth=auth)


def get_basic_auth_class() -> Optional[type]:  # pragma: no cover - trivial accessor
    """Expose the BasicAuth class when available, otherwise return None."""

    return _ExtendBasicAuth
