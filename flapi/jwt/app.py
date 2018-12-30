import json
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import flask

from . import coder, errors, store


class JwtHandler:

    header_key = "Authorization"
    token_prefix = "Bearer "
    encoding = "utf8"

    default_lifespan = 300
    default_algorithm = "HS256"

    validation_error = errors.JWTValidationError
    json_encoder: Optional[json.JSONEncoder] = None

    _jwt_store = store.JwtStore
    _handler_store = store.HandlerStore
    _jwt_coder = coder.Coder

    def __init__(self, app=None):
        self.app = None
        self.init_app(app)

    @property
    def secret(self):
        return self.app.config.get("FLAPI_JWT_SECRET", None)

    @property
    def lifespan(self):
        return self.app.config.get("FLAPI_JWT_LIFESPAN", None)

    @property
    def algorithm(self):
        return self.app.config.get("FLAPI_JWT_ALGORITHM", None)

    @property
    def issuer(self):
        return self.app.config.get("FLAPI_JWT_ISSUER", None)

    @property
    def audience(self):
        return self.app.config.get("FLAPI_JWT_AUDIENCE", None)

    @property
    def verify(self):
        return self.app.config.get("FLAPI_JWT_VERIFY", True)

    @property
    def auto_update(self):
        return self.app.config.get("FLAPI_JWT_AUTO_UPDATE", False)

    def init_app(self, app: flask.Flask) -> None:
        if app is not None:
            app.before_first_request(self.on_setup)
            app.before_request(self.before_request)
            app.after_request(self.after_request)
        self.app = app

    def on_setup(self):
        if self.secret is None:
            raise ValueError()  # TODO secret or algorithm is None

    def before_request(self) -> None:
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

    def after_request(self, response: flask.Response) -> flask.Response:
        self._handler_store.clear()
        if self.auto_update:
            prefix = self.token_prefix
            token_dict = self._jwt_store.get()
            print(token_dict)
            if token_dict:
                encoded = self._encode(token_dict)
                response.headers.set(self.header_key, f"{prefix}{encoded}")
        return response

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

    def _encode(
        self,
        token: Dict,
        algorithm: str = None,
        headers: Optional[Dict] = None,
        not_before: float = None,
        lifespan: int = None,
    ) -> str:
        lifespan: int = self.__load_param(lifespan, "lifespan")
        algorithm: str = self.__load_param(algorithm, "algorithm")

        token["exp"] = time.time() + lifespan
        if self.issuer and "iss" not in token:
            token["iss"]: str = self.issuer
        if self.audience and "aud" not in token:
            token["aud"]: str = self.audience
        if not_before and "nbf" not in token:
            token["nbf"]: float = not_before

        token_bytes: bytes = self._jwt_coder.encode(
            token, self.secret, algorithm, headers, self.json_encoder
        )
        return token_bytes.decode(self.encoding)

    def _decode(self, jwt_string: str) -> Dict:
        token_bytes: bytes = jwt_string.encode(self.encoding)
        return self._jwt_coder.decode(
            token_bytes,
            self.secret,
            [self.algorithm],
            self.verify,
            issuer=self.issuer,
            audience=self.audience,
        )

    def __load_param(self, defined: Any, name: str) -> Any:
        var: Any = defined or getattr(self, f"{name}", None)
        if var is not None:
            # TODO log warning using default {name}
            return var
        return getattr(self, f"default_{name}", None)
