import unittest
from flapi.jwt.rules import JWTRule


class AllOfTest(unittest.TestCase):
    def test_raises_not_implemented(self):
        self.assertRaises(NotImplementedError, JWTRule(), "token")
