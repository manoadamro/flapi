import copy
import datetime
import functools
import re
from typing import Any, Callable, ClassVar, Dict, List, Pattern, Tuple, Type, Union

from . import errors
from ..core import rules

AllOf = rules.AllOf
AnyOf = rules.AnyOf
NoneOf = rules.NoneOf
Callback = rules.Callback


class _Range:
    def __init__(
        self,
        minimum: Union[
            List, Tuple, str, int, float, datetime.datetime, datetime.date, None
        ],
        maximum: Union[
            List, Tuple, str, int, float, datetime.datetime, datetime.date, None
        ],
    ):
        self.min = minimum
        self.max = maximum

    def __call__(
        self,
        value: Union[
            List, Tuple, str, int, float, datetime.datetime, datetime.date, None
        ],
    ) -> bool:

        if value is None:
            return True
        if isinstance(value, (list, tuple, str)):
            value = len(value)

        minimum = self.min() if callable(self.min) else self.min
        maximum = self.max() if callable(self.max) else self.max

        if minimum is None and maximum is None:
            return True
        if minimum is None:
            return value <= maximum
        if maximum is None:
            return value >= minimum
        return minimum <= value <= maximum


class Schema:
    def __init__(self):
        self.object = Object(
            self.__class__,
            strict=self._is_strict,
            nullable=False,
            default=None,
            callback=None,
        )

    @property
    def _is_strict(self) -> bool:
        return getattr(self, "__strict__", False)

    def __call__(self, value: Dict) -> Dict:
        return self.object(value)


class Property(rules.Rule):
    def __init__(
        self,
        *types: Type[Any],
        nullable: bool = True,
        default: Any = None,
        callback: Callable = None,
    ):
        self.types = types
        self.nullable = nullable
        self.default = default
        self.callback = callback

    def _get_value(self, value: Any) -> Any:
        if value is not None:
            return value
        if not self.nullable and self.default is None:
            raise errors.SchemaValidationError("value should not be None")
        if callable(self.default):
            return self.default()
        return self.default

    def __call__(self, value: Any) -> Any:
        value = self._get_value(value)
        if (
            value is not None
            and len(self.types) > 0
            and not isinstance(value, self.types)
        ):
            raise errors.SchemaValidationError(
                f"value: {value} is not of expected type"
            )
        if self.callback is not None:
            return self.callback(value)
        return value


class CustomProperty(Property):
    def __init__(self, *args: Type, **kwargs: Any):
        super(CustomProperty, self).__init__(*args, **kwargs)

    def __call__(self, func: ClassVar[Callable]) -> Callable:
        @functools.wraps(func)
        def _wrapped(value: Any):
            value: Any = super(CustomProperty, self).__call__(value)
            return func(func.__class__, value)

        return _wrapped


class Object(Property):
    def __init__(self, schema: Type[Schema], strict: bool = False, **kwargs):
        super(Object, self).__init__(dict, **kwargs)
        self.strict = strict or schema._is_strict
        self.schema = self._load(schema)

    @classmethod
    def _load(cls, schema: Type[Schema]) -> Dict:
        return {f: getattr(schema, f) for f in dir(schema) if not f.startswith("_")}

    def _valid_fields(self, obj: Dict) -> bool:
        return all(key in self.schema for key in obj)

    def _valid_values(self, obj: Dict) -> Dict:
        return {key: func(obj.get(key, None)) for key, func in self.schema.items()}

    def __call__(self, value: Union[Dict, None]) -> Union[Dict, None]:
        value = super(Object, self).__call__(value)
        if value is None:
            return None
        if self.strict and not self._valid_fields(value):
            raise errors.SchemaValidationError("object contains extra fields")
        return self._valid_values(value)


class Array(Property):
    def __init__(
        self,
        schema: Union[Property, Type[Property]],
        min_length: Union[int, Callable] = None,
        max_length: Union[int, Callable] = None,
        callback=None,
    ):
        super(Array, self).__init__(list, nullable=False, default=[], callback=callback)
        self.schema = schema() if isinstance(schema, type) else schema
        self.range = _Range(min_length, max_length)

    def __call__(self, value: Union[List[Any], None]) -> Union[List[Any], None]:
        value = super(Array, self).__call__(value)
        if not self.range(value):
            raise errors.SchemaValidationError(f"value {value} is out of defined range")
        for i in range(len(value)):
            value[i] = self.schema(value[i])
        return value


class Choice(Property):
    def __init__(self, choices: List[Any], **kwargs: Any):
        super(Choice, self).__init__(**kwargs)
        self.choices = choices

    def __call__(self, value: Any) -> Any:
        value = super(Choice, self).__call__(value)
        if value is None:
            return None
        for choice in self.choices:
            if isinstance(choice, Property):
                try:
                    return choice(copy.deepcopy(value))
                except errors.SchemaValidationError:
                    continue
            elif value == choice:
                return value

        raise errors.SchemaValidationError()


class Number(Property):
    def __init__(
        self,
        types: Tuple = (int, float),
        min_value: Union[int, float, Callable] = None,
        max_value: Union[int, float, Callable] = None,
        **kwargs,
    ):
        super(Number, self).__init__(*types, **kwargs)
        self.range = _Range(min_value, max_value)

    def __call__(self, value: Union[int, float, None]) -> Union[int, float, None]:
        value = super(Number, self).__call__(value)
        if not self.range(value):
            raise errors.SchemaValidationError(f"value {value} is out of defined range")
        return value


class Int(Number):
    def __init__(self, **kwargs):
        super(Int, self).__init__((int,), **kwargs)


class Float(Number):
    def __init__(self, **kwargs):
        super(Float, self).__init__((int, float), **kwargs)


class Bool(Property):
    def __init__(self, **kwargs):
        super(Bool, self).__init__(bool, **kwargs)

    def __call__(self, value: Union[bool, None]) -> bool:
        return super(Bool, self).__call__(value)


class String(Property):
    def __init__(
        self,
        min_length: Union[int, float, Callable] = None,
        max_length: Union[int, float, Callable] = None,
        **kwargs,
    ):
        super(String, self).__init__(str, **kwargs)
        self.range = _Range(min_length, max_length)

    def __call__(self, value: Union[str, None]) -> Union[str, None]:
        value = super(String, self).__call__(value)
        if not self.range(value):
            raise errors.SchemaValidationError(f"value {value} is out of defined range")
        return value


class Regex(String):
    def __init__(self, matcher: Union[Pattern, str], **kwargs):
        super(Regex, self).__init__(**kwargs)
        self.matcher = re.compile(matcher) if isinstance(matcher, str) else matcher

    def _match(self, value: str):
        return re.match(self.matcher, value) is not None

    def __call__(self, value: Union[str, None]) -> Union[str, None]:
        value = super(Regex, self).__call__(value)
        if value is not None and not self._match(value):
            raise errors.SchemaValidationError(f"value {value} is out of defined range")
        return value


class Email(Regex):
    matcher = re.compile(".+@[^@]+.[^@]{2,}$")

    def __init__(self, **kwargs):
        super(Email, self).__init__(self.matcher, **kwargs)


class Uuid(Regex):
    matcher = re.compile(
        "^[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12}$"
    )

    def __init__(self, strip_hyphens=False, **kwargs):
        super(Uuid, self).__init__(self.matcher, **kwargs)
        self.strip_hyphens = strip_hyphens

    def __call__(self, value: Union[str, None]) -> Union[str, None]:
        value = super(Uuid, self).__call__(value)
        if value is not None and self.strip_hyphens:
            return value.replace("-", "")
        return value


class Date(Property):

    date_format = "%Y-%m-%d"

    def __init__(
        self,
        min_value: Union[datetime.date, Callable] = None,
        max_value: Union[datetime.date, Callable] = None,
        **kwargs,
    ):
        super(Date, self).__init__(datetime.date, **kwargs)
        self.range = _Range(min_value, max_value)

    @classmethod
    def _parse_date(cls, value: str):
        if "T" in value:
            value = value.split("T")[0]
        return datetime.datetime.strptime(value, cls.date_format).date()

    @classmethod
    def _get_date(
        cls, value: Union[str, float, int, datetime.datetime, datetime.date, None]
    ) -> Union[datetime.date, None]:
        try:
            if value is None:
                return None
            if isinstance(value, (float, int)) and value not in (True, False):
                return datetime.date.fromtimestamp(value)
            if isinstance(value, str):
                return cls._parse_date(value)
            if isinstance(value, datetime.datetime):
                return value.date()
            if isinstance(value, datetime.date):
                return value
            raise errors.SchemaValidationError(
                f"value: {value} is not of expected type"
            )
        except ValueError as ex:
            raise errors.SchemaValidationError(str(ex))

    def __call__(
        self, value: Union[str, float, int, datetime.date, datetime.datetime, None]
    ) -> Union[str, datetime.date, None]:
        value = self._get_date(value)
        value = super(Date, self).__call__(value)
        if not self.range(value):
            raise errors.SchemaValidationError(f"value {value} is out of defined range")
        return value


class DateTime(Property):

    timezone_matcher = re.compile(r"^.*?[+|\-][0-9]{2}:[0-9]{2}$")
    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"

    def __init__(
        self,
        min_value: Union[datetime.datetime, Callable] = None,
        max_value: Union[datetime.datetime, Callable] = None,
        **kwargs,
    ):
        super(DateTime, self).__init__(datetime.datetime, **kwargs)
        self.range = _Range(min_value, max_value)

    @classmethod
    def _parse_datetime(cls, value: str):

        if value.endswith("Z"):
            value = f"{value[:-1]}+00:00"

        if re.match(cls.timezone_matcher, value) is None:
            timezone = datetime.timezone.utc

        else:
            value, timezone_string = value[:-6], value[-6:]
            symbol, timezone_string = timezone_string[0], timezone_string[1:]
            hours, minutes = timezone_string.split(":")

            hours = int(hours)
            minutes = int(minutes)

            if symbol == "-":
                hours = -hours
                minutes = -minutes

            if hours == 0 and minutes == 0:
                timezone = datetime.timezone.utc
            else:
                delta = datetime.timedelta(hours=hours, minutes=minutes)
                timezone = datetime.timezone(delta)

        datetime_object = datetime.datetime.strptime(value, cls.datetime_format)
        return datetime_object.replace(tzinfo=timezone)

    @classmethod
    def _get_datetime(
        cls, value: Union[str, float, int, datetime.datetime, None]
    ) -> Union[datetime.datetime, None]:
        try:
            if value is None:
                return None
            if isinstance(value, (float, int)) and value not in (True, False):
                return datetime.datetime.fromtimestamp(value)
            if isinstance(value, str):
                return cls._parse_datetime(value)
            if isinstance(value, datetime.datetime):
                return value
            raise errors.SchemaValidationError(
                f"value: {value} is not of expected type"
            )
        except ValueError as ex:
            raise errors.SchemaValidationError(str(ex))

    def __call__(
        self, value: Union[str, float, int, datetime.datetime, None]
    ) -> Union[str, datetime.datetime, None]:
        value = self._get_datetime(value)
        value = super(DateTime, self).__call__(value)
        if not self.range(value):
            raise errors.SchemaValidationError(f"value {value} is out of defined range")
        return value
