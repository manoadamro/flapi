import unittest
import unittest.mock

from flapi.jwt.errors import JWTValidationError
from flapi.jwt.handler import JwtHandler
from flapi.jwt.protection import Protect


class ProtectTest(unittest.TestCase):
    def test_protected(self):
        rules = [lambda t: True, lambda t: True]
        with unittest.mock.patch.object(JwtHandler, "current_token", lambda: "token"):
            protected = Protect(*rules)
            self.assertTrue(protected(lambda: True)())

    def test_no_token(self):
        rules = [lambda t: True, lambda t: True]
        with unittest.mock.patch.object(JwtHandler, "current_token", lambda: None):
            protected = Protect(*rules)
            self.assertRaises(JWTValidationError, protected(lambda: True))

    def test_fails_rule(self):
        rules = [lambda t: True, lambda t: False]
        with unittest.mock.patch.object(JwtHandler, "current_token", lambda: "token"):
            protected = Protect(*rules)
            self.assertRaises(JWTValidationError, protected(lambda: True))
