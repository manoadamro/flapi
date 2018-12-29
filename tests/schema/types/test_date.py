import datetime
import unittest

import flapi.schema.errors
import flapi.schema.types


class DateTest(unittest.TestCase):

    epoc = datetime.date(year=1970, month=1, day=1)
    millenium = datetime.date(year=2000, month=1, day=1)
    millenium05 = datetime.date(year=2005, month=1, day=1)

    def test_from_timestamp(self):
        prop = flapi.schema.types.Date()
        self.assertEqual(prop(1545827395.914913), datetime.date(2018, 12, 26))

    def test_from_string(self):
        prop = flapi.schema.types.Date()
        self.assertEqual(prop("2018-12-26"), datetime.date(2018, 12, 26))

    def test_from_datetime_string(self):
        prop = flapi.schema.types.Date()
        self.assertEqual(prop("2018-12-26T00:00:00.000Z"), datetime.date(2018, 12, 26))

    def test_from_datetime(self):
        prop = flapi.schema.types.Date()
        self.assertEqual(
            prop(datetime.datetime(2018, 12, 26, 12, 29, 55, 914913)),
            datetime.date(2018, 12, 26),
        )

    def test_date_wrong_type(self):
        prop = flapi.schema.types.Date()
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, True)

    def test_min_only(self):
        prop = flapi.schema.types.Date(min_value=self.epoc)
        self.assertEqual(prop(self.millenium), self.millenium)

    def test_min_only_out_of_range(self):
        prop = flapi.schema.types.Date(min_value=self.millenium)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, self.epoc)

    def test_max_only(self):
        prop = flapi.schema.types.Date(max_value=self.millenium05)
        self.assertEqual(prop(self.millenium), self.millenium)

    def test_max_only_out_of_range(self):
        prop = flapi.schema.types.Date(max_value=self.millenium)
        self.assertRaises(
            flapi.schema.errors.SchemaValidationError, prop, self.millenium05
        )

    def test_min_and_max(self):
        prop = flapi.schema.types.Date(min_value=self.epoc, max_value=self.millenium05)
        self.assertEqual(prop(self.millenium), self.millenium)

    def test_min_and_max_out_of_range(self):
        prop = flapi.schema.types.Date(min_value=self.epoc, max_value=self.millenium)
        self.assertRaises(
            flapi.schema.errors.SchemaValidationError, prop, self.millenium05
        )

    def test_no_range(self):
        prop = flapi.schema.types.Date()
        self.assertEqual(prop(self.epoc), self.epoc)

    # PROPERTY TESTS

    def test_nullable_by_default(self):
        prop = flapi.schema.types.Date()
        self.assertIsNone(prop(None))

    def test_nullable_allows_null(self):
        prop = flapi.schema.types.Date(nullable=True)
        self.assertIsNone(prop(None))

    def test_nullable_raises_error(self):
        prop = flapi.schema.types.Date(nullable=False)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, None)

    def test_default_is_none(self):
        prop = flapi.schema.types.Date(default=None)
        self.assertIsNone(prop(None))

    def test_default_value(self):
        prop = flapi.schema.types.Date(default=self.epoc)
        self.assertEqual(prop(None), self.epoc)

    def test_default_passive_when_value_not_none(self):
        prop = flapi.schema.types.Date(default=self.epoc)
        self.assertEqual(prop(self.millenium), self.millenium)

    def test_default_callable(self):
        prop = flapi.schema.types.Date(default=lambda: self.millenium)
        self.assertEqual(prop(None), self.millenium)

    def test_wrong_type(self):
        prop = flapi.schema.types.Date(callback=None)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, "nope")

    def test_callback(self):
        prop = flapi.schema.types.Date(
            callback=lambda v: v + datetime.timedelta(days=5)
        )
        self.assertEqual(prop(self.epoc), datetime.date(year=1970, month=1, day=6))

    def test_no_callback(self):
        prop = flapi.schema.types.Date(callback=None)
        self.assertEqual(prop(self.epoc), self.epoc)
