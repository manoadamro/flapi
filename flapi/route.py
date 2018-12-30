from typing import List, Tuple, Union

import flask

from . import jwt, schema


class Route:
    def __init__(
        self,
        base: Union[flask.Flask, flask.Blueprint],
        json: Union[schema.Schema] = None,
        auth: Union[jwt.JWTRule, List, Tuple] = None,
    ):
        self.base = base
        self.schema = json
        self.auth = auth

    def __call__(self, func):
        if self.auth is not None:
            func = jwt.protect(*self.auth)(func)
        if self.schema is not None:
            func = schema.protect(self.schema)(func)
        return self.base(func)
