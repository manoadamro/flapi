import unittest
from flapi.jwt.rules import JwtRule


class AllOfTest(unittest.TestCase):
    def test_raises_not_implemented(self):
        self.assertRaises(NotImplementedError, JwtRule(), "token")
