import unittest

import flapi.schema.errors
import flapi.schema.types


class EmailTest(unittest.TestCase):
    def test_fails_invalid_email_missing_at(self):
        prop = flapi.schema.types.Email()
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, "1234.5")

    def test_fails_invalid_email_missing_dot(self):
        prop = flapi.schema.types.Email()
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, "12@345")

    def test_min_only(self):
        prop = flapi.schema.types.Email(min_length=0)
        self.assertEqual(prop("12@34.5"), "12@34.5")

    def test_min_only_out_of_range(self):
        prop = flapi.schema.types.Email(min_length=10)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, "12@34.5")

    def test_max_only(self):
        prop = flapi.schema.types.Email(max_length=10)
        self.assertEqual(prop("12@34.5"), "12@34.5")

    def test_max_only_out_of_range(self):
        prop = flapi.schema.types.Email(max_length=10)
        self.assertRaises(
            flapi.schema.errors.SchemaValidationError, prop, "1234@512345123451234.5"
        )

    def test_min_and_max(self):
        prop = flapi.schema.types.Email(min_length=0, max_length=10)
        self.assertEqual(prop("12@34.5"), "12@34.5")

    def test_min_and_max_out_of_range(self):
        prop = flapi.schema.types.Email(min_length=0, max_length=10)
        self.assertRaises(
            flapi.schema.errors.SchemaValidationError, prop, "1234@512345123451234.5"
        )

    def test_no_range(self):
        prop = flapi.schema.types.Email()
        self.assertEqual(prop("1234@512345123451234.5"), "1234@512345123451234.5")

    # PROPERTY TESTS

    def test_nullable_by_default(self):
        prop = flapi.schema.types.Email()
        self.assertIsNone(prop(None))

    def test_nullable_allows_null(self):
        prop = flapi.schema.types.Email(nullable=True)
        self.assertIsNone(prop(None))

    def test_nullable_raises_error(self):
        prop = flapi.schema.types.Email(nullable=False)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, None)

    def test_default_is_none(self):
        prop = flapi.schema.types.Email(default=None)
        self.assertIsNone(prop(None))

    def test_default_value(self):
        prop = flapi.schema.types.Email(default="12@34.5")
        self.assertEqual(prop(None), "12@34.5")

    def test_default_passive_when_value_not_none(self):
        prop = flapi.schema.types.Email(default="pey")
        self.assertEqual(prop("12@34.5"), "12@34.5")

    def test_default_callable(self):
        prop = flapi.schema.types.Email(default=lambda: "12@34.5")
        self.assertEqual(prop(None), "12@34.5")

    def test_wrong_type(self):
        prop = flapi.schema.types.Email(callback=None)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, 12)

    def test_callback(self):
        prop = flapi.schema.types.Email(callback=lambda v: f"1a2@34.5")
        self.assertEqual(prop("12@34.5"), "1a2@34.5")

    def test_no_callback(self):
        prop = flapi.schema.types.Email(callback=None)
        self.assertEqual(prop("12@34.5"), "12@34.5")
