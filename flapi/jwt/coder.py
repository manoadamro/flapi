import json
import jwt
from typing import Any, Dict, Optional, List
from . import errors


class Coder:

    decode_error = errors.JWTDecodeError
    encode_error = errors.JWTEncodeError

    @classmethod
    def decode(
        cls,
        jwt_bytes: bytes,
        secret: str,
        algorithms: List[str],
        verify: bool = True,
        options: Optional[Dict] = None,
        **validate: Any,
    ) -> Dict:
        try:
            return jwt.decode(
                jwt_bytes, secret, verify, algorithms, options, **validate
            )
        except jwt.PyJWTError as ex:
            raise cls.decode_error(ex)

    @classmethod
    def encode(
        cls,
        token: Dict,
        secret: str,
        algorithm: str,
        headers: Optional[Dict] = None,
        json_encoder: Optional[json.JSONEncoder] = None,
    ) -> bytes:
        try:
            return jwt.encode(token, secret, algorithm, headers, json_encoder)
        except jwt.PyJWTError as ex:
            raise cls.encode_error(ex)
