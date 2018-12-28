from typing import Any, Callable, Dict
import functools
from . import errors, rules, builder


class JwtProtected:
    def __init__(self, *rules: rules.JWTRule):
        self.rules = rules

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            token: Dict = builder.Builder.current_token()
            if not token:
                raise errors.JWTValidationError(
                    "client did not supply a token in request header"
                )
            if not all(rule(token) for rule in self.rules):
                raise errors.JWTValidationError(
                    "one or more checks on the supplied jwt failed"
                )
            return func(*args, **kwargs)

        return wrapper
