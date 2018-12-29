from typing import Dict, Union

import flask


class Store:

    key = "jwt"

    @classmethod
    def set(cls, token: Union[Dict, None]) -> None:
        setattr(flask.g, cls.key, token)

    @classmethod
    def get(cls) -> Union[Dict, None]:
        return getattr(flask.g, cls.key, None)
