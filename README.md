[![CircleCI](https://circleci.com/gh/manoadamro/flapi/tree/master.svg?style=svg)](https://circleci.com/gh/manoadamro/flapi/tree/master)
[![Coverage Status](https://coveralls.io/repos/github/manoadamro/flapi/badge.svg?branch=master)](https://coveralls.io/github/manoadamro/flapi?branch=master)
[![CodeFactor](https://www.codefactor.io/repository/github/manoadamro/flapi/badge)](https://www.codefactor.io/repository/github/manoadamro/flapi)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Supported Versions

- 3.6
- 3.7

## Installation

```
pip3 install --upgrade pip
pip3 install git+http://github.com/manoadamro/flapi
```

## Packages

- [flapi](#Flapi)
- [flapi.jwt](#JWT)
- [flapi.schema](#Schema)

---

# Flapi

---

# JWT

```python
from flapi.jwt import FlaskJwt, jwt_protected, HasScopes, MatchValue

jwt_handler = FlaskJwt("secret", lifespan=300)

def get_token():
    encoded_token = jwt_handler.generate_token({"uuid": "123"}, ["read:protected"])
    return {"jwt": token}

@jwt_protected(HasScopes("read:protected"))
def protected():
    return "success"

@jwt_protected(HasScopes("read:protected"), MatchValue("jwt:uuid", "url:uuid"))
def protected_user(uuid):
    return uuid
```

- [FlaskJwt](#FlaskJwt)
  - [constructor](#constructor)
  - [generate_token](#generate_token)
  - [current_token](#current_token)
- [protected_route](#protected_route)
  - [JwtRule](#JwtRule)
  - [HasScopes](#HasScopes)
  - [MatchValue](#MatchValue)
  - [Callback](#Callback)
  - [AnyOf](#AnyOf)
  - [AllOf](#AllOf)
  - [NoneOf](#NoneOf)

## FlaskJwt(...)

Creates an instance of FlaskJwt

```python
jwt_handler = FlaskJwt(secret, lifespan, **kwargs)
```

__secret__: str (required) String used to sign tokens.

__lifespan__: int (required) Lifespan of a token in seconds, after which it will be considered invalid

__app__: flask.Flask (default: None):Instance of a flask app (flask.Flask). If one is provided it will be initialised immediately

__verify__: bool (default: True) If false, token rules will not be verified.

__auto_update__: bool (default: False) Return a token with an updated expiry in every response to a request that contained a valid jwt.

__algorithm__: str (default: HS256) Algorithm used to sign tokens.

__issuer__: str, list, callable (default: None) Limit token usage by issuer or list of issuers. can be callable returning string or list of strings

__audience__: str, list, callable (default: None) Limit token usage by audience or list of audiences. can be callable returning string or list of strings

__json_encoder__: json.JSONEncoder (default: None) Json encoder used to serialise dicts

## FlaskJwt.generate_token(...)

Generates a new token, stores the decoded version in global store (can be retrieved with `FlaskJwt.current_token()`) and returns the encoded version

```python
jwt_handler = FlaskJwt(...)
jwt_handler.generate_token(fields, scopes, **kwargs)
```

__fields__: dict (required) Token body

__scopes__: list, callable (default: ()) List of string scopes eg. `read:thing`, `write:thing`. can be callable returning list of strings

__algorithm__: str (default: HS256) Algorithm used to sign tokens.

__headers__: dict (default: None) Token headers

__not_before__: float (default: None) UTC timestamp representing the earliest time that the token will be considered valid

__lifespan__: int (defalut: constructor definition) Lifespan of a token in seconds, after which it will be considered invalid. defaults to lifespan defined in constructor if not defined, otherwise overrides it.


## FlaskJwt.current_token()

Returns the decoded token associated with the current request from global store

```python
FlaskJwt.current_token()
```

## protected_route(...)

```python
@protected_route(*rules)
def some_method():
    ...
```

__rules__: one or more rules. see [flapi.jwt.rules](#flapi.jwt.rules)


# JWT Rules

## JwtRule(...)

Base class for all JWT rules.
<br>
Can be used to build custom rules

```python

class CustomRule(JwtRule):
    """
    A simple example to show to to extend JwtRule
    Ensures a token contains all of the keys defined in constructor
    """
    def __init__(*expected_keys: Any):
        """
        constructor:
        defines a list of keys that must exist in a token
        """
        self.expected_keys: List[str] = expected_keys

    def __call__(self, token: Dict) -> bool:
        """
        call:
        must be implemented.
        takes a decoded token (dict).
        returns True or False
        """
        return all(i in token.items() for i in self.expected_keys())


rule = CustomRule("thing", "other_thing"):

rule({"thing" 123, "nope": 321})
False

rule({"thing" 123, "other_thing": 321})
True

```

If `__call__` method is not implemented in a subclass of JwtRule, a `NotImplementedException` will be raised.

## HasScopes(...)

Ensures that a token contains all of the defined scopes

```python

rule = HasScopes("read:thing", "write:thing"):

rule({"some": "thing", "other": 123, "scp": ["read:thing", "write:other"]})
False

rule({"some": "thing", "other": 123, "scp": ["read:thing", "write:thing"]})
True
```

## MatchValue(...)

Uses `jsonpointer` to ensure that two or more values are the same.
<br>
valid objects are:

- __header__ : flask.request.header
- __json__ : flask.request.json
- __url__ : flask.request.view_args
- __param__ : flask.request.args
- __form__ : flask.request.form
- __jwt__ : the active token

```python

# url: /some/page/<id>
# id: "12345"

rule = MatchValue("jwt:id", "url:id")


rule({"id": "54321"})
False

rule({"id": "12345"})
True


rule = MatchValue("jwt:thing/id", "url:id")

rule({"thing": {"id": "12345"}})
True

rule({"id": "12345"})
False

```

## Callback(...)

Takes one or more callables that must all return True in order for the check to be considered a pass.

```python

def yes(token):
    return True

def no(token):
    return False


rule = Callback(no)

rule({"some": "thing"})
False


rule = Callback(yes)

rule({"some": "thing"})
True


```

## AnyOf(...)

Considers the check passed if any of the defined rules pass

```python

rule = AnyOf(
    HasScopes("read:thing", "write:thing"),
    MatchValue("jwt:id", "url:id"))

rule({"scp": ["read:thing", "write:other"]})
True

rule({"id": "54321"})
True

rule({"some": "thing"})
False
```

## AllOf(...)

Considers the check passed if all of the defined rules pass

```python

# url: /some/page/<id>
# id: "12345"

rule = AllOf(
    HasScopes("read:thing", "write:thing"),
    MatchValue("jwt:id", "url:id"))

rule({"scp": ["read:thing", "write:other"]})
False

rule({"id": "54321"})
False

rule({"id": "54321", "scp": ["read:thing", "write:other"]})
True
```

## NoneOf(...)

Considers the check passed if none of the defined rules pass

```python

# url: /some/page/<id>
# id: "12345"

rule = AllOf(
    HasScopes("read:thing", "write:thing"),
    MatchValue("jwt:id", "url:id"))

rule({"scp": ["read:thing", "write:other"]})
False

rule({"id": "54321"})
False

rule({"id": "54321", "scp": ["read:thing", "write:other"]})
False

rule({"some": "thing"})
True
```

---

# Planned Improvements:

### JWT

- Allow MatchValue to use custom objects, probably accept tuple (callable, path) in place of string path.
- Pass strings to jwt_protected and have them implicitly used as required scopes.
- Pass a tuple to any collection rule and have it implicitly used as an AllOf
- Allow more parameters to be resolved callables

---
