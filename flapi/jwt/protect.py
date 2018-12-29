import functools
from typing import Any, Callable, Dict

from . import builder, errors, rules


class Protect:
    def __init__(self, *checks: rules.JwtRule):
        self.checks = rules.AllOf(*checks)

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            token: Dict = builder.Builder.current_token()
            if not token:
                raise errors.JWTValidationError(
                    "client did not supply a token in request header"
                )
            if not self.checks(token):
                raise errors.JWTValidationError(
                    "one or more checks on the supplied jwt failed"
                )
            return func(*args, **kwargs)

        return wrapper
