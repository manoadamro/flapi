import unittest

import flapi.schema.errors
import flapi.schema.types


class NumberTest(unittest.TestCase):
    def test_property_choice(self):
        prop = flapi.schema.types.Choice(
            [flapi.schema.types.Bool(), flapi.schema.types.Int()]
        )
        self.assertEqual(prop(12), 12)
        self.assertEqual(prop(True), True)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, 4.5)

    def test_invalid_choice(self):
        prop = flapi.schema.types.Choice([1, 2, 3])
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, 4)

    def test_nullable_by_default(self):
        prop = flapi.schema.types.Choice([1, 2, 3])
        self.assertIsNone(prop(None))

    def test_nullable_allows_null(self):
        prop = flapi.schema.types.Choice([1, 2, 3], nullable=True)
        self.assertIsNone(prop(None))

    def test_nullable_raises_error(self):
        prop = flapi.schema.types.Choice([1, 2, 3], nullable=False)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, None)

    def test_default_is_none(self):
        prop = flapi.schema.types.Choice([1, 2, 3], default=None)
        self.assertIsNone(prop(None))

    def test_default_value(self):
        prop = flapi.schema.types.Choice([1, 2, 3], default=2)
        self.assertEqual(prop(None), 2)

    def test_default_passive_when_value_not_none(self):
        prop = flapi.schema.types.Choice([1, 2, 3], default=2)
        self.assertEqual(prop(1), 1)

    def test_default_callable(self):
        prop = flapi.schema.types.Choice([1, 2, 3], default=lambda: 1)
        self.assertEqual(prop(None), 1)

    def test_wrong_type(self):
        prop = flapi.schema.types.Choice([1, 2, 3], callback=None)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, "nope")

    def test_callback(self):
        prop = flapi.schema.types.Choice([1, 2, 3], callback=lambda v: v * 2)
        self.assertEqual(prop(1), 2)

    def test_no_callback(self):
        prop = flapi.schema.types.Choice([1, 2, 3], callback=None)
        self.assertEqual(prop(1), 1)
