import datetime
import unittest

import flapi.schema.errors
import flapi.schema.types


class DateTimeTest(unittest.TestCase):

    epoc = datetime.datetime(year=1970, month=1, day=1)
    millenium = datetime.datetime(year=2000, month=1, day=1)
    millenium05 = datetime.datetime(year=2005, month=1, day=1)

    def test_from_timestamp(self):
        prop = flapi.schema.types.DateTime()
        self.assertEqual(
            prop(1545827395.914913), datetime.datetime(2018, 12, 26, 12, 29, 55, 914913)
        )

    def test_from_string(self):
        prop = flapi.schema.types.DateTime()
        self.assertEqual(
            prop("2018-12-26T00:00:00.000"),
            datetime.datetime(2018, 12, 26, 0, 0, 0, 0, tzinfo=datetime.timezone.utc),
        )

    def test_from_string_with_timezone(self):
        prop = flapi.schema.types.DateTime()
        self.assertEqual(
            prop("2018-12-26T00:00:00.000-10:00"),
            datetime.datetime(
                2018,
                12,
                26,
                0,
                0,
                0,
                0,
                tzinfo=datetime.timezone(datetime.timedelta(hours=-10)),
            ),
        )

    def test_bad_timezone_symbol(self):
        prop = flapi.schema.types.DateTime()
        self.assertRaises(
            flapi.schema.errors.SchemaValidationError,
            prop,
            "2018-12-26T00:00:00.000$10:00",
        )

    def test_from_string_with_z(self):
        prop = flapi.schema.types.DateTime()
        self.assertEqual(
            prop("2018-12-26T00:00:00.000Z"),
            datetime.datetime(2018, 12, 26, 0, 0, 0, 0, tzinfo=datetime.timezone.utc),
        )

    def test_wrong_datetime_type(self):
        prop = flapi.schema.types.DateTime()
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, True)

    def test_min_only(self):
        prop = flapi.schema.types.DateTime(min_value=self.epoc)
        self.assertEqual(prop(self.millenium), self.millenium)

    def test_min_only_out_of_range(self):
        prop = flapi.schema.types.DateTime(min_value=self.millenium)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, self.epoc)

    def test_max_only(self):
        prop = flapi.schema.types.DateTime(max_value=self.millenium05)
        self.assertEqual(prop(self.millenium), self.millenium)

    def test_max_only_out_of_range(self):
        prop = flapi.schema.types.DateTime(max_value=self.millenium)
        self.assertRaises(
            flapi.schema.errors.SchemaValidationError, prop, self.millenium05
        )

    def test_min_and_max(self):
        prop = flapi.schema.types.DateTime(
            min_value=self.epoc, max_value=self.millenium05
        )
        self.assertEqual(prop(self.millenium), self.millenium)

    def test_min_and_max_out_of_range(self):
        prop = flapi.schema.types.DateTime(
            min_value=self.epoc, max_value=self.millenium
        )
        self.assertRaises(
            flapi.schema.errors.SchemaValidationError, prop, self.millenium05
        )

    def test_no_range(self):
        prop = flapi.schema.types.DateTime()
        self.assertEqual(prop(self.epoc), self.epoc)

    # PROPERTY TESTS

    def test_nullable_by_default(self):
        prop = flapi.schema.types.DateTime()
        self.assertIsNone(prop(None))

    def test_nullable_allows_null(self):
        prop = flapi.schema.types.DateTime(nullable=True)
        self.assertIsNone(prop(None))

    def test_nullable_raises_error(self):
        prop = flapi.schema.types.DateTime(nullable=False)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, None)

    def test_default_is_none(self):
        prop = flapi.schema.types.DateTime(default=None)
        self.assertIsNone(prop(None))

    def test_default_value(self):
        prop = flapi.schema.types.DateTime(default=self.epoc)
        self.assertEqual(prop(None), self.epoc)

    def test_default_passive_when_value_not_none(self):
        prop = flapi.schema.types.DateTime(default=self.epoc)
        self.assertEqual(prop(self.millenium), self.millenium)

    def test_default_callable(self):
        prop = flapi.schema.types.DateTime(default=lambda: self.millenium)
        self.assertEqual(prop(None), self.millenium)

    def test_wrong_type(self):
        prop = flapi.schema.types.DateTime(callback=None)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, "nope")

    def test_callback(self):
        prop = flapi.schema.types.DateTime(
            callback=lambda v: v + datetime.timedelta(days=5)
        )
        self.assertEqual(prop(self.epoc), datetime.datetime(year=1970, month=1, day=6))

    def test_no_callback(self):
        prop = flapi.schema.types.DateTime(callback=None)
        self.assertEqual(prop(self.epoc), self.epoc)
