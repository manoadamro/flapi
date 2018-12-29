import unittest

from flapi.core.rules import Rule


class RuleTest(unittest.TestCase):
    def test_raises_not_implemented(self):
        self.assertRaises(NotImplementedError, Rule(), "token")
