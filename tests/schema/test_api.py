import datetime
import re

import flask
import flask_testing

from flapi import schema

bp = flask.Blueprint(__name__, "test_bp")


def get_minimum_dob():
    return (datetime.datetime.utcnow() - datetime.timedelta(days=365.25 * 16)).date()


class Address(schema.Schema):
    number = schema.Int(min_value=0, nullable=False)
    post_code = schema.Regex(
        re.compile("[a-zA-z]{2}[0-9] ?[0-9][a-zA-z]{2}"), nullable=False
    )


class Items(schema.Schema):
    name = schema.String(min_length=3, max_length=50, nullable=False)
    count = schema.Int(min_value=0, default=0)


class Person(schema.Schema):
    name = schema.String(min_length=3, max_length=50, nullable=False)
    address = schema.Object(Address, nullable=False, strict=True)
    friends = schema.Array(schema.Uuid, default=[])
    items = schema.Array(schema.Object(Items, strict=False), default=[])
    date_of_birth = schema.Date(max_value=get_minimum_dob, nullable=False)
    date_of_death = schema.Date(max_value=datetime.date.today, nullable=True)

    @schema.custom_property(int, float, nullable=False)
    def something(cls, value):
        if not isinstance(value, (int, float)):
            raise TypeError
        return value * 2


@bp.route("/", methods=["POST"])
@schema.protect(Person)
def create_person(person):
    return flask.jsonify(person)


class ApiTest(flask_testing.TestCase):
    def create_app(self):
        app = flask.Flask(__name__)
        app.register_blueprint(bp)
        return app

    def test_minimal(self):
        self.assert200(
            self.client.post(
                "/",
                json={
                    "name": "dave",
                    "address": {"post_code": "AB1 2CD", "number": 123},
                    "date_of_birth": "1970-01-01",
                    "something": 321,
                },
            )
        )

    def test_strict(self):
        self.assert500(
            self.client.post(
                "/",
                json={
                    "name": "dave",
                    "address": {"post_code": "AB1 2CD", "number": 123, "nope": True},
                    "date_of_birth": "1970-01-01",
                    "something": 321,
                },
            )
        )

    def test_callable_min(self):
        self.assert500(
            self.client.post(
                "/",
                json={
                    "name": "dave",
                    "address": {"post_code": "AB1 2CD", "number": 123},
                    "date_of_birth": "2010-01-01",
                    "something": 321,
                },
            )
        )

    def test_custom_prop_fails(self):
        self.assert500(
            self.client.post(
                "/",
                json={
                    "name": "dave",
                    "address": {"post_code": "AB1 2CD", "number": 123},
                    "date_of_birth": "2010-01-01",
                    "something": "nope",
                },
            )
        )
