import time
from typing import Any, Callable, Dict, List, Tuple, Union

import flask

from . import base, store


class JwtHandler(base.BaseHandler):
    default_lifespan = 300
    default_algorithm = "HS256"

    _jwt_store = store.JwtStore
    _handler_store = store.HandlerStore

    def __init__(self, app=None):
        super(JwtHandler, self).__init__()
        self.init_app(app)

    @classmethod
    def current_token(cls) -> Union[Dict, None]:
        return cls._jwt_store.get()

    @classmethod
    def current_handler(cls):
        return cls._handler_store.get()

    @classmethod
    def generate_token(
        cls, fields: Dict[str, Any], scopes: Union[List, Tuple, Callable] = (), **kwargs
    ) -> str:
        fields["iat"] = time.time()
        fields["scp"] = scopes if not callable(scopes) else scopes()
        app: __class__ = cls.current_handler()
        app._jwt_store.set(fields)
        return app._encode(fields, **kwargs)

    def init_app(self, app: flask.Flask) -> None:
        if app is not None:
            app.before_first_request(self._on_setup)
            app.before_request(self._before_request)
            app.after_request(self._after_request)
        self.app = app

    def _on_setup(self):
        if self.secret is None:
            raise ValueError()  # TODO secret or algorithm is None

    def _before_request(self) -> None:
        self._handler_store.set(self)
        prefix = self.token_prefix
        token_string = flask.request.headers.get(self.header_key, None)
        if token_string is not None:
            if not token_string.startswith(prefix) or len(token_string) <= len(prefix):
                raise self.validation_error("invalid bearer token")
            token_string = token_string[len(prefix) :]
            decoded = self._decode(token_string)
            self._jwt_store.set(decoded)
        else:
            self._jwt_store.set(None)

    def _after_request(self, response: flask.Response) -> flask.Response:
        self._handler_store.clear()
        if self.auto_update:
            prefix = self.token_prefix
            token_dict = self._jwt_store.get()
            if token_dict:
                encoded = self._encode(token_dict)
                response.headers.set(self.header_key, f"{prefix}{encoded}")
        return response
