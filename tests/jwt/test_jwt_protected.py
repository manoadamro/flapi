import unittest
import unittest.mock
from flapi.jwt.route import JwtProtected
from flapi.jwt.builder import Builder
from flapi.jwt.errors import JWTValidationError


class JWTProtectedTest(unittest.TestCase):
    def test_protected(self):
        rules = [lambda t: True, lambda t: True]
        with unittest.mock.patch.object(Builder, "current_token", lambda: "token"):
            protected = JwtProtected(*rules)
            self.assertTrue(protected(lambda: True)())

    def test_no_token(self):
        rules = [lambda t: True, lambda t: True]
        with unittest.mock.patch.object(Builder, "current_token", lambda: None):
            protected = JwtProtected(*rules)
            self.assertRaises(JWTValidationError, protected(lambda: True))

    def test_fails_rule(self):
        rules = [lambda t: True, lambda t: False]
        with unittest.mock.patch.object(Builder, "current_token", lambda: "token"):
            protected = JwtProtected(*rules)
            self.assertRaises(JWTValidationError, protected(lambda: True))
