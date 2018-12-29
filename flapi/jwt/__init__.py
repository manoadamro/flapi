from . import app as _app
from . import protect as _protect
from . import rules as _rules
from . import errors as _errors

JwtHandler = _app.JwtHandler
current_handler = JwtHandler.current_handler
current_token = JwtHandler.current_token
generate_token = JwtHandler.generate_token

protect = _protect.Protect

JWTRule = _rules.JwtRule
HasScopes = _rules.HasScopes
MatchValue = _rules.MatchValue

AllOf = _rules.AllOf
AnyOf = _rules.AnyOf
NoneOf = _rules.NoneOf

JWTEncodeError = _errors.JWTEncodeError
JWTDecodeError = _errors.JWTDecodeError
JWTValidationError = _errors.JWTValidationError
