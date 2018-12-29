import unittest

import flapi.schema.errors
import flapi.schema.types


class UuidTest(unittest.TestCase):
    def test_fails_invalid_uuid(self):
        prop = flapi.schema.types.Uuid()
        self.assertRaises(
            flapi.schema.errors.SchemaValidationError,
            prop,
            "9689c6bd-8cfa-4888-a92c-7d23599b94",
        )

    def test_strip_hyphens(self):
        prop = flapi.schema.types.Uuid(strip_hyphens=True)
        self.assertEqual(
            prop("9689c6bd-8cfa-4888-a92c-7d23599b94aa"),
            "9689c6bd8cfa4888a92c7d23599b94aa",
        )

    # PROPERTY TESTS

    def test_nullable_by_default(self):
        prop = flapi.schema.types.Uuid()
        self.assertIsNone(prop(None))

    def test_nullable_allows_null(self):
        prop = flapi.schema.types.Uuid(nullable=True)
        self.assertIsNone(prop(None))

    def test_nullable_raises_error(self):
        prop = flapi.schema.types.Uuid(nullable=False)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, None)

    def test_default_is_none(self):
        prop = flapi.schema.types.Uuid(default=None)
        self.assertIsNone(prop(None))

    def test_default_value(self):
        prop = flapi.schema.types.Uuid(default="9689c6bd-8cfa-4888-a92c-7d23599b94aa")
        self.assertEqual(prop(None), "9689c6bd-8cfa-4888-a92c-7d23599b94aa")

    def test_default_passive_when_value_not_none(self):
        prop = flapi.schema.types.Uuid(default="9689c6bd-8cfa-4888-a92c-7d23599b94ab")
        self.assertEqual(
            prop("9689c6bd-8cfa-4888-a92c-7d23599b94aa"),
            "9689c6bd-8cfa-4888-a92c-7d23599b94aa",
        )

    def test_default_callable(self):
        prop = flapi.schema.types.Uuid(
            default=lambda: "9689c6bd-8cfa-4888-a92c-7d23599b94aa"
        )
        self.assertEqual(prop(None), "9689c6bd-8cfa-4888-a92c-7d23599b94aa")

    def test_wrong_type(self):
        prop = flapi.schema.types.Uuid(callback=None)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, 12)

    def test_callback(self):
        prop = flapi.schema.types.Uuid(
            callback=lambda v: f"9689c6bd-8cfa-4888-a92c-7d23599b94ab"
        )
        self.assertEqual(
            prop("9689c6bd-8cfa-4888-a92c-7d23599b94aa"),
            "9689c6bd-8cfa-4888-a92c-7d23599b94ab",
        )

    def test_no_callback(self):
        prop = flapi.schema.types.Uuid(callback=None)
        self.assertEqual(
            prop("9689c6bd-8cfa-4888-a92c-7d23599b94aa"),
            "9689c6bd-8cfa-4888-a92c-7d23599b94aa",
        )
