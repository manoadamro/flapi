import json
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from . import coder, store


class Builder:

    store = store.Store
    coder = coder.Coder
    encoding: str = "utf8"

    def __init__(
        self,
        secret: str,
        lifespan: int,
        algorithm: str = "HS256",
        issuer: Union[str, List[str], Callable] = None,
        audience: Union[str, List[str], Callable] = None,
        json_encoder: Optional[json.JSONEncoder] = None,
    ):
        self.secret = secret
        self.lifespan = lifespan
        self.algorithm = algorithm
        self.issuer = issuer if not callable(issuer) else issuer()
        self.audience = audience if not callable(audience) else audience()
        self.json_encoder = json_encoder

    def encode(
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
        token_bytes: bytes = self.coder.encode(
            token, self.secret, algorithm or self.algorithm, headers, self.json_encoder
        )
        return token_bytes.decode(self.encoding)

    def decode(
        self,
        jwt_string: str,
        verify: bool = True,
        algorithms: List[str] = None,
        options: Optional[Dict] = None,
    ) -> Dict:
        token_bytes: bytes = jwt_string.encode(self.encoding)
        return self.coder.decode(
            token_bytes,
            self.secret,
            algorithms or [self.algorithm],
            verify,
            options,
            issuer=self.issuer,
            audience=self.audience,
        )

    @classmethod
    def current_token(cls) -> Union[Dict, None]:
        return cls.store.get()

    def generate_token(
        self,
        fields: Dict[str, Any],
        scopes: Union[List, Tuple, Callable] = (),
        *args,
        **kwargs
    ) -> str:
        fields["iat"] = time.time()
        fields["scp"] = scopes if not callable(scopes) else scopes()
        self.store.set(fields)
        return self.encode(fields, *args, **kwargs)
