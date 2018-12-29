import json
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import flask

from . import coder, errors, store


class JwtHandler:

    header_key = "Authorization"
    token_prefix = "Bearer "
    encoding = "utf8"
    default_algorithm = "HS256"

    validation_error = errors.JWTValidationError
    json_encoder: Optional[json.JSONEncoder] = None

    _store = store.Store
    _coder = coder.Coder

    def __init__(self, app=None):
        self.app = None
        self.init_app(app)

    @property
    def secret(self):
        return self.app.config.get("JWT_SECRET", None)

    @secret.setter
    def secret(self, value):
        self.app.config["JWT_SECRET"] = value

    @property
    def lifespan(self):
        return self.app.config.get("JWT_LIFESPAN", None)

    @lifespan.setter
    def lifespan(self, value):
        self.app.config["JWT_LIFESPAN"] = value

    @property
    def algorithm(self):
        return self.app.config.get("JWT_ALGORITHM", self.default_algorithm)

    @algorithm.setter
    def algorithm(self, value):
        self.app.config["JWT_ALGORITHM"] = value

    @property
    def issuer(self):
        return self.app.config.get("JWT_ISSUER", None)

    @property
    def audience(self):
        return self.app.config.get("JWT_AUDIENCE", None)

    @property
    def options(self):
        return self.app.config.get("JWT_OPTIONS", None)

    @property
    def verify(self):
        return self.app.config.get("JWT_VERIFY", True)

    @property
    def auto_update(self):
        return self.app.config.get("JWT_AUTO_UPDATE", False)

    def init_app(self, app: flask.Flask) -> None:
        if app is not None:
            app.before_first_request(self.on_setup)
            app.before_request(self.before_request)
            app.after_request(self.after_request)
        self.app = app

    def on_setup(self):
        if self.secret is None or self.lifespan is None or self.algorithm is None:
            raise ValueError()

    def before_request(self) -> None:
        prefix = self.token_prefix
        token_string = flask.request.headers.get(self.header_key, None)
        if token_string is not None:
            if not token_string.startswith(prefix) or len(token_string) <= len(prefix):
                raise self.validation_error("invalid bearer token")
            token_string = token_string[len(prefix) :]
            decoded = self._decode(token_string)
            self._store.set(decoded)
        else:
            self._store.set(None)

    def after_request(self, response: flask.Response) -> flask.Response:
        if self.auto_update:
            prefix = self.token_prefix
            token_dict = self._store.get()
            print(token_dict)
            if token_dict:
                encoded = self._encode(token_dict)
                response.headers.set(self.header_key, f"{prefix}{encoded}")
        return response

    @classmethod
    def current_token(cls) -> Union[Dict, None]:
        return cls._store.get()

    def generate_token(
        self,
        fields: Dict[str, Any],
        scopes: Union[List, Tuple, Callable] = (),
        **kwargs,
    ) -> str:
        fields["iat"] = time.time()
        fields["scp"] = scopes if not callable(scopes) else scopes()
        self._store.set(fields)
        return self._encode(fields, **kwargs)

    def _encode(
        self,
        token: Dict,
        algorithm: str = None,
        headers: Optional[Dict] = None,
        not_before: float = None,
        lifespan: int = None,
    ) -> str:
        token["exp"] = time.time() + (lifespan or self.lifespan)
        if self.issuer and "iss" not in token:
            token["iss"]: str = self.issuer
        if self.audience and "aud" not in token:
            token["aud"]: str = self.audience
        if not_before and "nbf" not in token:
            token["nbf"]: float = not_before
        token_bytes: bytes = self._coder.encode(
            token, self.secret, algorithm or self.algorithm, headers, self.json_encoder
        )
        return token_bytes.decode(self.encoding)

    def _decode(self, jwt_string: str) -> Dict:
        token_bytes: bytes = jwt_string.encode(self.encoding)
        return self._coder.decode(
            token_bytes,
            self.secret,
            [self.algorithm],
            self.verify,
            self.options,
            issuer=self.issuer,
            audience=self.audience,
        )
