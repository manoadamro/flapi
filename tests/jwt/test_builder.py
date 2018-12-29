import time
import unittest
import unittest.mock

import flask
import jwt

from flapi.jwt.app import JwtHandler


class BuilderTest(unittest.TestCase):

    algorithm = "HS256"
    secret = "secret"
    lifespan = 10

    class FakeError(jwt.PyJWTError):
        pass

    @property
    def jwt(self):
        return {"some": "thing"}

    def encode(self, data):
        return self.handler._coder.encode(
            data, self.handler.secret, algorithm=self.handler.algorithm
        ).decode(self.handler.encoding)

    def setUp(self):
        self.app = flask.Flask(__name__)
        self.handler = JwtHandler(self.app)
        self.handler.lifespan = self.lifespan
        self.handler.secret = self.secret
        self.handler.algorithm = self.algorithm
        self.handler._coder.encode_error = self.FakeError
        self.handler._coder.decode_error = self.FakeError

    def test_encode_minimal(self):
        data = self.jwt
        token = self.handler._encode(data)
        self.assertIsInstance(token, str)

    def test_encode_with_expiry_already_in_token(self):
        data = self.jwt
        data["exp"] = "nope"
        self.handler._encode(data)
        self.assertIsInstance(data["exp"], float)

    def test_encode_with_issuer(self):
        self.handler.app.config["JWT_ISSUER"] = "some_issuer"
        data = self.jwt
        self.handler._encode(data)
        self.assertEqual(data["iss"], "some_issuer")

    def test_encode_with_issuer_already_in_token(self):
        self.handler.app.config["JWT_ISSUER"] = "some_issuer"
        data = self.jwt
        data["iss"] = "some_other_issuer"
        self.handler._encode(data)
        self.assertEqual(data["iss"], "some_other_issuer")

    def test_encode_with_audience(self):
        self.handler.app.config["JWT_AUDIENCE"] = "some_audience"
        data = self.jwt
        self.handler._encode(data)
        self.assertEqual(data["aud"], "some_audience")

    def test_encode_with_audience_already_in_token(self):
        self.handler.app.config["JWT_AUDIENCE"] = "some_audience"
        data = self.jwt
        data["aud"] = "some_other_audience"
        self.handler._encode(data)
        self.assertEqual(data["aud"], "some_other_audience")

    def test_encode_with_not_before(self):
        data = self.jwt
        self.handler._encode(data, not_before=12.3)
        self.assertEqual(data["nbf"], 12.3)

    def test_encode_with_not_before_already_in_token(self):
        data = self.jwt
        data["nbf"] = 32.1
        self.handler._encode(data, not_before=12.3)
        self.assertEqual(data["nbf"], 32.1)

    @unittest.mock.patch("time.time", lambda: 0)
    def test_encode_with_all(self):
        self.maxDiff = 1000
        data = self.jwt

        self.handler.lifespan = 10
        self.handler.app.config["JWT_ISSUER"] = "some_issuer"
        self.handler.app.config["JWT_AUDIENCE"] = "some_audience"
        self.handler._encode(data, not_before=12.3)

        expected = {
            "some": "thing",
            "exp": 10,
            "iss": "some_issuer",
            "aud": "some_audience",
            "nbf": 12.3,
        }

        self.assertTrue(
            all(k in data for k in expected)
            and all(k in expected for k in data)
            and all(expected[k] == data[k] for k in data),
            f"{data} != {expected}",
        )

    def test_decode_with_invalid_issuer(self):
        self.handler.app.config["JWT_ISSUER"] = "some_issuer"
        data = self.jwt
        data["iss"] = "nope"
        token = self.encode(data)
        self.assertRaises(self.FakeError, self.handler._decode, token)

    def test_decode_with_invalid_audience(self):
        self.handler.app.config["JWT_ISSUER"] = "some_issuer"
        data = self.jwt
        data["aud"] = "nope"
        token = self.encode(data)
        self.assertRaises(self.FakeError, self.handler._decode, token)

    def test_decode_with_invalid_not_before(self):
        data = self.jwt
        data["nbf"] = time.time() + 10
        token = self.encode(data)
        self.assertRaises(self.FakeError, self.handler._decode, token)

    def test_decode(self):
        data = self.jwt
        token = self.encode(data)
        token = self.handler._decode(token)
        self.assertIsInstance(token, dict)
