import jwt


class FlaskJWTError(jwt.PyJWTError, PermissionError):
    """
    base class for jwt related errors
    """

    ...


class JWTDecodeError(FlaskJWTError):
    """
    raised when the decoding of a jwt fails
    """

    ...


class JWTEncodeError(FlaskJWTError):
    """
    raised when the encoding of a jwt fails
    """

    ...


class JWTValidationError(FlaskJWTError):
    """
    raised when the validation of a jwt fails
    """

    ...
