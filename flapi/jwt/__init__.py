from . import app as _app, route as _route, rules as _rules, errors as _errors

FlaskJwt = _app.FlaskJwt
current_token = FlaskJwt.current_token

jwt_protected = _route.JwtProtected

JWTRule = _rules.JwtRule
HasScopes = _rules.HasScopes
MatchValue = _rules.MatchValue
AllOf = _rules.AllOf
AnyOf = _rules.AnyOf
NoneOf = _rules.NoneOf

JWTEncodeError = _errors.JWTEncodeError
JWTDecodeError = _errors.JWTDecodeError
JWTValidationError = _errors.JWTValidationError
