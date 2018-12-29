import unittest

import flapi.schema.errors
import flapi.schema.types


class BasicSchema(flapi.schema.types.Schema):
    thing = flapi.schema.types.Bool()


class ArrayTest(unittest.TestCase):
    def test_min_only(self):
        prop = flapi.schema.types.Array(flapi.schema.types.Bool, min_length=0)
        self.assertEqual(prop([True, True]), [True, True])

    def test_min_only_out_of_range(self):
        prop = flapi.schema.types.Array(flapi.schema.types.Bool, min_length=1)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, [])

    def test_max_only(self):
        prop = flapi.schema.types.Array(flapi.schema.types.Bool, max_length=3)
        self.assertEqual(prop([True, True]), [True, True])

    def test_max_only_out_of_range(self):
        prop = flapi.schema.types.Array(flapi.schema.types.Bool, max_length=3)
        self.assertRaises(
            flapi.schema.errors.SchemaValidationError, prop, [True, True, True, True]
        )

    def test_min_and_max(self):
        prop = flapi.schema.types.Array(
            flapi.schema.types.Bool, min_length=0, max_length=3
        )
        self.assertEqual(prop([True, True]), [True, True])

    def test_min_and_max_out_of_range(self):
        prop = flapi.schema.types.Array(
            flapi.schema.types.Bool, min_length=0, max_length=3
        )
        self.assertRaises(
            flapi.schema.errors.SchemaValidationError, prop, [True, True, True, True]
        )

    def test_no_range(self):
        prop = flapi.schema.types.Array(flapi.schema.types.Bool)
        self.assertEqual(prop([True, True, True, True]), [True, True, True, True])

    def test_array_of_property(self):
        prop = flapi.schema.types.Array(flapi.schema.types.Bool)
        self.assertEqual(prop([True, True]), [True, True])

    def test_array_of_property_fails(self):
        prop = flapi.schema.types.Array(flapi.schema.types.Bool)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, [True, ""])

    def test_wrong_type(self):
        prop = flapi.schema.types.Array(BasicSchema, callback=None)
        self.assertRaises(flapi.schema.errors.SchemaValidationError, prop, 12)

    def test_callback(self):
        prop = flapi.schema.types.Array(
            BasicSchema, callback=lambda v: [{"thing": True}]
        )
        self.assertEqual(prop([{"thing": False}, {"thing": False}]), [{"thing": True}])

    def test_no_callback(self):
        prop = flapi.schema.types.Array(BasicSchema, callback=None)
        self.assertEqual(prop([{"thing": False}]), [{"thing": False}])
