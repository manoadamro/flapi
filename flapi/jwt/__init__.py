from . import handler
from . import protection
from . import rules
from . import errors
from . import base

JwtHandler = handler.JwtHandler
SimpleJwtHandler = base.BaseHandler

current_handler = JwtHandler.current_handler
current_token = JwtHandler.current_token
generate_token = JwtHandler.generate_token

protect = protection.Protect

JWTRule = rules.JwtRule
HasScopes = rules.HasScopes
MatchValue = rules.MatchValue

AllOf = rules.AllOf
AnyOf = rules.AnyOf
NoneOf = rules.NoneOf

JWTEncodeError = errors.JWTEncodeError
JWTDecodeError = errors.JWTDecodeError
JWTValidationError = errors.JWTValidationError
