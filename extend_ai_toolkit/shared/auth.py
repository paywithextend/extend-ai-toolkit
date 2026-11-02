"""Construction helpers for the supported Extend SDK."""

from extend import ExtendClient
from extend.auth import Authorization, BasicAuth


def supports_authorization() -> bool:
    return True


def build_basic_auth(api_key: str, api_secret: str):
    return BasicAuth(api_key, api_secret)


def create_extend_client(
    api_key: str,
    api_secret: str,
    auth: Authorization | None = None,
    *,
    environment: str | None = None,
) -> ExtendClient:
    return ExtendClient(
        auth=auth if auth is not None else BasicAuth(api_key, api_secret), environment=environment
    )


def create_client_with_auth(auth: Authorization, *, environment: str | None = None) -> ExtendClient:
    return ExtendClient(auth=auth, environment=environment)


def get_basic_auth_class():
    return BasicAuth
