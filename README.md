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

## Docs

- [flapi](#Flapi)
- [flapi.jwt](#JWT)
- [flapi.schema](#Schema)

[Planned Improvements](#Planned-Improvements)

---

# Flapi

TODO

---

# JWT

```python
jwt_handler = FlaskJwt("secret", lifespan=300)

def get_token():
    encoded_token = jwt_handler.generate_token({"uuid": "123"}, ["read:protected"])
    return {"jwt": token}

@protect(HasScopes("read:protected"))
def protected():
    return "success"

@protect(HasScopes("read:protected"), MatchValue("jwt:uuid", "url:uuid"))
def protected_user(uuid):
    return uuid
```

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

## protect(...)

```python
@protect(*rules)
def some_method():
    ...
```

__rules__: one or more rules. see [flapi.jwt.rules](#JWT-Rules)

---

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

Considers the check passed if any of the defined rule pass

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

Considers the check passed if all of the defined rule pass

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

Considers the check passed if none of the defined rule pass

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

# Schema

```python

def get_minimum_dob():
    return (datetime.datetime.utcnow() - datetime.timedelta(days=365.25 * 16)).date()


class Address(Schema):
    number = Int(min_value=0, nullable=False)
    post_code = Regex(
        re.compile("[a-zA-z]{2}[0-9] ?[0-9][a-zA-z]{2}"), nullable=False
    )


class Items(Schema):
    name = String(min_length=3, max_length=50, nullable=False)
    count = Int(min_value=0, default=0)


class Person(Schema):
    __strict__ = True
    name = String(min_length=3, max_length=50, nullable=False)
    address = Object(Address, nullable=False, strict=True)
    friends = Array(Uuid, default=[])
    items = Array(Object(Items, strict=False), default=[])
    date_of_birth = Date(max_value=get_minimum_dob, nullable=False)
    date_of_death = Date(max_value=datetime.date.today, nullable=True)

    @custom_property(int, float, nullable=False)
    def something(cls, value):
        return value * 2
```

## Schema(...)

Base class for schema definitions

```python

class MySchema(Schema):
    ...

```

Notes:

- Anything (including methods) defined in schema classes will be considered a property.
 If you wish to hide an attribute/method you will need to prefix it with an underscore

- You can define properties using a method without the `@custom_property` decorator.
 This will mean you are passed value with no checks having been done on it.

- To mark a schema as "strict" (meaning extra keys are not accepted),
 add `__strict__ = True` as an attribute

## protect(...)

```python
@protect(MySchema)
def some_method(obj):
    ...
```

__schema__: Schema, Property or Rule (required) The check that has to pass in order for the decorated method to be called. see [flapi.schema.types](#Schema-Types)

---

# Schema Types

## Property(...)

Base class for all JWT rules.
<br>
Can be used to build custom property

```python
class MyProperty:
    def __init__(self, multiplier, **kwargs):
        # call super and tell Property we only accept ints or floats,
        # pass on any kwargs
        super(DateTime, self).__init__(int, float, **kwargs)
        self.multiplier = multiplier

    def __call__(self, item):
        # do the default checks by calling super(),
        # get back an updated value
        value = super(Array, self).__call__(value)

        # do the property thing
        return value * multiplier

```

__types__: tuple of types (required) Accepted value types

__nullable__: bool (default True) If false, an error will be raised if a null value is receeved

__default__: Any (default None) If a null value is a received, it will be replaced with this

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

## custom_property(...)

Does the same as [Property](#Property) but as a decorator!

```python
@custom_property(int, float, nullable=False)
def something(cls, value):
    return value * 2

@custom_property(int, float, default=1)
def something_else(cls, value):
    return value * 3
```

__types__: tuple of types (required) Accepted value types

__nullable__: bool (default True) If false, an error will be raised if a null value is receeved

__default__: Any (default None) If a null value is a received, it will be replaced with this

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

## Object(...)

Allows nesting of schemas

```python
class Address(Schema):
    number = Int(min_value=0, nullable=False)
    post_code = Regex(
        re.compile("[a-zA-z]{2}[0-9] ?[0-9][a-zA-z]{2}"), nullable=False
    )

class Person(Schema):
    address = Object(Address, nullable=False, strict=True)
```

__strict__: bool (default False) overrides `__strict__` attribute on schema definition

__nullable__: bool (default True) If false, an error will be raised if a null value is receeved

__default__: Any (default None) If a null value is a received, it will be replaced with this

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

## Array(...)

Defines an array of items conforming to a Schema/Property definition

```python
class MySchema(Schema):
    items = Array(Object(Item, strict=False), default=[])
```

__min_length__: Property or Rule (required)

__min_length__: int or callable returning int (default None) Minimum allowed array length

__max_length__: int or callable returning int (default None) Maximum allowed array length

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

Notes:

- Value will default to an empty array if none

## Choice(...)

Ensures a value is equal to one from a defined set.

```python
class MySchema(Schema):
    choice = Choice([Bool(), Int(), "1", "2"], nullable=False)
```

__choices__: list (required) A list containing specific valid values, Property definitions or a mix of the two.

__nullable__: bool (default True) If false, an error will be raised if a null value is receeved

__default__: Any (default None) If a null value is a received, it will be replaced with this

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

Notes:

- If a value conforms to more than one choice, it will be validated against the first valid one.

## Number(...)

Ensures a value is either an in or a float

```python
class MySchema(Schema):
    number = Number(min_value=0, max_value=10, nullable=False, default=2)
```

__min_value__: int, float or callable returning int or float (default None) Minimum allowed value

__max_value__: int, float or callable returning int or float (default None) Maximum allowed value

__nullable__: bool (default True) If false, an error will be raised if a null value is receeved

__default__: Any (default None) If a null value is a received, it will be replaced with this

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

## Int(...)

Ensures a value is an integer

```python
class MySchema(Schema):
    number = Int(min_value=0, max_value=10, nullable=False, default=2)
```

__min_value__: int or callable returning int (default None) Minimum allowed value

__max_value__: int or callable returning int (default None) Maximum allowed value

__nullable__: bool (default True) If false, an error will be raised if a null value is receeved

__default__: Any (default None) If a null value is a received, it will be replaced with this

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

## Float(...)

Ensures a value is a float

```python
class MySchema(Schema):
    number = Float(min_value=0.0, max_value=6.5, nullable=False, default=2.5)
```

__min_value__: float or callable returning float (default None) Minimum allowed value

__max_value__: float or callable returning float (default None) Maximum allowed value

__nullable__: bool (default True) If false, an error will be raised if a null value is receeved

__default__: Any (default None) If a null value is a received, it will be replaced with this

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

## Bool(...)

Ensures a value is either true or false

```python
class MySchema(Schema):
    boolean = Bool(nullable=False, default=True)
```

__nullable__: bool (default True) If false, an error will be raised if a null value is receeved

__default__: Any (default None) If a null value is a received, it will be replaced with this

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

## String(...)

Ensures a value is a string

```python
class MySchema(Schema):
    thing = String(min_length=2, max_length=5, nullable=False)
```

__min_length__: int or callable returning int (default None) Minimum allowed string length

__max_length__: int or callable returning int (default None) Maximum allowed string length

__nullable__: bool (default True) If false, an error will be raised if a null value is receeved

__default__: Any (default None) If a null value is a received, it will be replaced with this

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

## Regex(...)

Ensures a value matches a regex string

```python
class MySchema(Schema):
    thing = Regex(".+@[^@]+.[^@]{2,}$", min_length=2, max_length=5, nullable=False)
```

__matcher__: regex string or compiled pattern (required) Regex to match value against

__min_length__: int or callable returning int (default None) Minimum allowed string length

__max_length__: int or callable returning int (default None) Maximum allowed string length

__nullable__: bool (default True) If false, an error will be raised if a null value is receeved

__default__: Any (default None) If a null value is a received, it will be replaced with this

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

## Email(...)

Ensures a value is a valid email address

```python
class MySchema(Schema):
    thing = Email(nullable=False)
```

__min_length__: int or callable returning int (default None) Minimum allowed string length

__max_length__: int or callable returning int (default None) Maximum allowed string length

__nullable__: bool (default True) If false, an error will be raised if a null value is receeved

__default__: Any (default None) If a null value is a received, it will be replaced with this

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

Notes:

- matcher used: `.+@[^@]+.[^@]{2,}$`

## Uuid(...)

Ensures a value is a valid uuid

```python
class MySchema(Schema):
    thing = Email(nullable=False, strip_hyphens=True)
```

__strip_hyphens__: bool (default False) If true, hyphens will be removed from the value string

__nullable__: bool (default True) If false, an error will be raised if a null value is receeved

__default__: Any (default None) If a null value is a received, it will be replaced with this

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

Notes:

- matcher used: `^[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12}$`

## Date(...)

Ensures a value is either a valid iso8601 date or utc timestamp and parses to date object

```python
class MySchema(Schema):
    date = Date(nullable=False, min_value=datetime.date.today)
```

__min_value__: date or callable returning date (default None) Minimum allowed date

__max_value__: date or callable returning date (default None) Maximum allowed date

__nullable__: bool (default True) If false, an error will be raised if a null value is receeved

__default__: Any (default None) If a null value is a received, it will be replaced with this

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

Notes:

- format used: `%Y-%m-%d`

## Datetime(...)

Ensures a value is a valid iso8601 datetime or utc timestamp and parses to datetime object

```python
class MySchema(Schema):
    time = DateTime(nullable=False, min_value=datetime.datetime.now)
```

__min_value__: datetime or callable returning datetime (default None) Minimum allowed datetime

__max_value__: datetime or callable returning datetime (default None) Maximum allowed datetime

__nullable__: bool (default True) If false, an error will be raised if a null value is receeved

__default__: Any (default None) If a null value is a received, it will be replaced with this

__callback__: Callable (default None) A method to call once all checks are complete.
This method receives the value as its only parameter and returns a modified value

Notes:

- format used: `%Y-%m-%dT%H:%M:%S.%f`

- accepts timezones in `hh:mm` format or `Z`

## AllOf(...)

TODO description

```python
# TODO example
```

TODO params

## AnyOf(...)

TODO description

```python
# TODO example
```

TODO params

## NoneOf(...)

TODO description

```python
# TODO example
```

TODO params

---

## Callback(...)

TODO description

```python
# TODO example
```

TODO params

---

# Planned Improvements:

### JWT

- Allow MatchValue to use custom objects, probably accept tuple (callable, path) in place of string path.
- Pass strings to jwt_protected and have them implicitly used as required scopes.
- Pass a tuple to any collection rule and have it implicitly used as an AllOf
- Allow more parameters to be resolved callables

### Schema

- Auto map to `sqlalchemy` model
- Auto map to `neomodel` model
- Define a key that is different to the attribute in schema class
- Allow more parameters to be resolved callables

---
