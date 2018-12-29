import flask
from typing import Dict, Union


class Store:

    key = "jwt"

    @classmethod
    def set(cls, token: Dict) -> None:
        setattr(flask.g, cls.key, token)

    @classmethod
    def get(cls) -> Union[Dict, None]:
        return getattr(flask.g, cls.key, None)
