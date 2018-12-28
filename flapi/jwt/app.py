from typing import Any
import flask
from . import builder, errors


class FlaskJwt(builder.Builder):

    header_key = "Authorization"
    token_prefix = "Bearer "
    validation_error = errors.JWTValidationError

    def __init__(
        self,
        secret: str,
        lifespan: int,
        verify: bool = True,
        auto_update: bool = False,
        app=None,
        **kwargs: Any,
    ):
        super(FlaskJwt, self).__init__(secret, lifespan, **kwargs)
        self.verify = verify
        self.auto_update = auto_update
        self.app = None

        self.init_app(app)

    def init_app(self, app: flask.Flask) -> None:
        if app is not None:
            app.before_request(self.pre_request_callback)
            app.after_request(self.post_request_callback)
        self.app = app

    def pre_request_callback(self) -> None:
        prefix = self.token_prefix
        token_string = flask.request.headers.get(self.header_key, None)
        if token_string is not None:
            if not token_string.startswith(prefix) or len(token_string) <= len(prefix):
                raise self.validation_error("invalid bearer token")
            token_string = token_string[len(prefix) :]
            decoded = self.decode(token_string, self.verify)
            self.store.set(decoded)
        else:
            self.store.set(None)

    def post_request_callback(self, response: flask.Response) -> flask.Response:
        if self.auto_update:
            prefix = self.token_prefix
            token_dict = self.store.get()
            if token_dict:
                encoded = self.encode(token_dict)
                response.headers.set(self.header_key, f"{prefix}{encoded}")
        return response
