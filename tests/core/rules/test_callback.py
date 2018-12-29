import unittest

from flapi.core.rules import Callback


class CallbackTest(unittest.TestCase):
    def test_all_of(self):
        rule = Callback(lambda _: True, lambda _: True)
        self.assertTrue(rule({}))

    def test_fails(self):
        rule = Callback(lambda _: True, lambda _: False)
        self.assertFalse(rule({}))
