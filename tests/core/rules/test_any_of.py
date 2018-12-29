import unittest

from flapi.core.rules import AnyOf


class AnyOfTest(unittest.TestCase):
    def test_any_of(self):
        rule = AnyOf(lambda _: True, lambda _: False)
        self.assertTrue(rule({}))

    def test_fails(self):
        rule = AnyOf(lambda _: False, lambda _: False)
        self.assertFalse(rule({}))
