import unittest

import flapi.schema.errors
import flapi.schema.types


class BoolTest(unittest.TestCase):
    def test_nullable_by_default(self):
        prop = flapi.schema.types.Bool()
        self.assertIsNone(prop(None))

    def test_nullable_allows_null(self):
        prop = flapi.schema.types.Bool(nullable=True)
        self.assertIsNone(prop(None))

    def test_nullable_raises_error(self):
        prop = flapi.schema.types.Bool(nullable=False)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, None)

    def test_default_is_none(self):
        prop = flapi.schema.types.Bool(default=None)
        self.assertIsNone(prop(None))

    def test_default_value(self):
        prop = flapi.schema.types.Bool(default=True)
        self.assertEqual(prop(None), True)

    def test_default_passive_when_value_not_none(self):
        prop = flapi.schema.types.Bool(default=False)
        self.assertEqual(prop(True), True)

    def test_default_callable(self):
        prop = flapi.schema.types.Bool(default=lambda: True)
        self.assertEqual(prop(None), True)

    def test_wrong_type(self):
        prop = flapi.schema.types.Bool(callback=None)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, 12)

    def test_callback(self):
        prop = flapi.schema.types.Bool(callback=lambda v: False)
        self.assertEqual(prop(True), False)

    def test_no_callback(self):
        prop = flapi.schema.types.Bool(callback=None)
        self.assertEqual(prop(True), True)
