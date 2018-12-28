import unittest
import unittest.mock
import jwt
import time
import flask
from flapi.jwt.builder import Builder


class BuilderTest(unittest.TestCase):

    secret = "secret"
    lifespan = 10

    class FakeError(jwt.PyJWTError):
        pass

    @property
    def jwt(self):
        return {"some": "thing"}

    @property
    def scopes(self):
        return "read:thing", "write:thing"

    def encode(self, data):
        return self.handler.coder.encode(
            data, self.handler.secret, algorithm=self.handler.algorithm
        ).decode(self.handler.encoding)

    def setUp(self):
        self.app = flask.Flask(__name__)
        self.handler = Builder(self.secret, self.lifespan)
        self.handler.coder.encode_error = self.FakeError
        self.handler.coder.decode_error = self.FakeError

    def test_encode_minimal(self):
        data = self.jwt
        token = self.handler.encode(data)
        self.assertIsInstance(token, str)

    def test_encode_with_expiry_already_in_token(self):
        data = self.jwt
        data["exp"] = "nope"
        self.handler.encode(data)
        self.assertIsInstance(data["exp"], float)

    def test_encode_with_issuer(self):
        data = self.jwt
        self.handler.issuer = "some_issuer"
        self.handler.encode(data)
        self.assertEqual(data["iss"], "some_issuer")

    def test_encode_with_issuer_already_in_token(self):
        data = self.jwt
        self.handler.issuer = "some_issuer"
        data["iss"] = "some_other_issuer"
        self.handler.encode(data)
        self.assertEqual(data["iss"], "some_other_issuer")

    def test_encode_with_audience(self):
        data = self.jwt
        self.handler.audience = "some_audience"
        self.handler.encode(data)
        self.assertEqual(data["aud"], "some_audience")

    def test_encode_with_audience_already_in_token(self):
        data = self.jwt
        self.handler.audience = "some_audience"
        data["aud"] = "some_other_audience"
        self.handler.encode(data)
        self.assertEqual(data["aud"], "some_other_audience")

    def test_encode_with_not_before(self):
        data = self.jwt
        self.handler.encode(data, not_before=12.3)
        self.assertEqual(data["nbf"], 12.3)

    def test_encode_with_not_before_already_in_token(self):
        data = self.jwt
        data["nbf"] = 32.1
        self.handler.encode(data, not_before=12.3)
        self.assertEqual(data["nbf"], 32.1)

    @unittest.mock.patch("time.time", lambda: 0)
    def test_encode_with_all(self):
        self.maxDiff = 1000
        data = self.jwt

        self.handler.lifespan = 10
        self.handler.issuer = "some_issuer"
        self.handler.audience = "some_audience"
        self.handler.encode(data, not_before=12.3)

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
        data = self.jwt
        data["iss"] = "nope"
        self.handler.issuer = "some_issuer"
        token = self.encode(data)
        self.assertRaises(self.FakeError, self.handler.decode, token)

    def test_decode_with_invalid_audience(self):
        data = self.jwt
        data["aud"] = "nope"
        self.handler.audience = "some_audience"
        token = self.encode(data)
        self.assertRaises(self.FakeError, self.handler.decode, token)

    def test_decode_with_invalid_not_before(self):
        data = self.jwt
        data["nbf"] = time.time() + 10
        token = self.encode(data)
        self.assertRaises(self.FakeError, self.handler.decode, token)

    def test_decode(self):
        data = self.jwt
        token = self.encode(data)
        token = self.handler.decode(token)
        self.assertIsInstance(token, dict)

    def test_current_token(self):
        expected = {"some": "thing"}
        with unittest.mock.patch.object(self.handler.store, "get", lambda: expected):
            token = self.handler.current_token()
        self.assertEqual(token, expected)

    def test_null_current_token(self):
        with unittest.mock.patch.object(self.handler.store, "get", lambda: None):
            token = self.handler.current_token()
        self.assertIsNone(token)

    def test_generate_token(self):
        with self.app.app_context():
            token_string = self.handler.generate_token(self.jwt, self.scopes)
        self.assertIsInstance(token_string, str)

    def test_generate_token_defaults_issued_at_time(self):
        with self.app.app_context():
            self.handler.generate_token(self.jwt, self.scopes)
            token = self.handler.current_token()
        self.assertIsInstance(token["iat"], float)

    def test_generate_token_includes_scopes(self):
        scopes = self.scopes
        with self.app.app_context():
            self.handler.generate_token(self.jwt, self.scopes)
            token = self.handler.current_token()
        self.assertEqual(token["scp"], scopes)
