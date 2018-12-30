import json
import time
from typing import Any, Dict, Optional

from . import coder, errors


class BaseHandler:

    header_key = "Authorization"
    token_prefix = "Bearer "
    encoding = "utf8"

    validation_error = errors.JWTValidationError
    json_encoder: Optional[json.JSONEncoder] = None

    _jwt_coder = coder.Coder

    def __init__(self, app=None):
        self.app = app

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
