import unittest
import unittest.mock
import jwt
from flapi.jwt.coder import Coder


class JWTCoderTest(unittest.TestCase):

    key = "secret"
    algorithm = "HS256"
    credentials = (key, algorithm)

    fake_jwt = {"some": "thing"}

    class FakeError(jwt.PyJWTError):
        pass

    def raise_error(self, *args, **kwargs):
        raise jwt.PyJWTError

    def setUp(self):
        self.coder = Coder
        self.coder.encode_error = self.FakeError
        self.coder.decode_error = self.FakeError

    def test_serialize_to_bytes(self):
        token = self.coder.encode(self.fake_jwt, *self.credentials)
        self.assertIsInstance(token, bytes)

    def test_deserialize(self):
        token = self.coder.encode(self.fake_jwt, *self.credentials)
        decoded = self.coder.decode(token, self.key, [self.algorithm], verify=False)
        self.assertEqual(self.fake_jwt, decoded)

    @unittest.mock.patch("jwt.encode", raise_error)
    def test_encode_error(self):
        self.assertRaises(
            self.FakeError, self.coder.encode, self.fake_jwt, *self.credentials
        )

    @unittest.mock.patch("jwt.decode", raise_error)
    def test_decode_error(self):
        self.assertRaises(
            self.FakeError, self.coder.decode, self.fake_jwt, *self.credentials
        )
