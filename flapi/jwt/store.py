from typing import Any

import flask


class _Store:

    key = None

    @classmethod
    def set(cls, token: Any) -> None:
        setattr(flask.g, cls.key, token)

    @classmethod
    def get(cls) -> Any:
        return getattr(flask.g, cls.key, None)

    @classmethod
    def clear(cls) -> None:
        setattr(flask.g, cls.key, None)


class JwtStore(_Store):
    key = "jwt"


class HandlerStore(_Store):
    key = "jwt_handler"
