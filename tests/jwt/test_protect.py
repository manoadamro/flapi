import unittest
import unittest.mock
from flapi.jwt.protect import Protect
from flapi.jwt.builder import Builder
from flapi.jwt.errors import JWTValidationError


class ProtectTest(unittest.TestCase):
    def test_protected(self):
        rules = [lambda t: True, lambda t: True]
        with unittest.mock.patch.object(Builder, "current_token", lambda: "token"):
            protected = Protect(*rules)
            self.assertTrue(protected(lambda: True)())

    def test_no_token(self):
        rules = [lambda t: True, lambda t: True]
        with unittest.mock.patch.object(Builder, "current_token", lambda: None):
            protected = Protect(*rules)
            self.assertRaises(JWTValidationError, protected(lambda: True))

    def test_fails_rule(self):
        rules = [lambda t: True, lambda t: False]
        with unittest.mock.patch.object(Builder, "current_token", lambda: "token"):
            protected = Protect(*rules)
            self.assertRaises(JWTValidationError, protected(lambda: True))
