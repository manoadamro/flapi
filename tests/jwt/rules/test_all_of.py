import unittest
from flapi.jwt.rules import AllOf


class AllOfTest(unittest.TestCase):
    def test_all_of(self):
        rule = AllOf(lambda _: True, lambda _: True)
        self.assertTrue(rule({}))

    def test_fails(self):
        rule = AllOf(lambda _: True, lambda _: False)
        self.assertFalse(rule({}))
