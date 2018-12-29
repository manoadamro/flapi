import unittest
import unittest.mock

import flask
import jwt

from flapi.jwt.app import FlaskJwt


class JwtTest(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)
        self.jwt = FlaskJwt("secret", 60, auto_update=True)
        self.jwt.init_app(self.app)
        self.jwt.validation_error = self.FakeError

    class FakeError(jwt.PyJWTError):
        pass

    def test_registers_pre(self):
        self.assertTrue(
            self.jwt.pre_request_callback in self.app.before_request_funcs[None],
            f"{self.jwt.pre_request_callback} not in {self.app.before_request_funcs}",
        )

    def test_pre_request_callback_null_token(self):
        with self.app.app_context(), unittest.mock.patch(
            "flask.request", unittest.mock.Mock(headers={})
        ):
            self.jwt.pre_request_callback()
            self.assertIsNone(self.jwt.store.get())

    def test_pre_request_callback_invalid_token(self):
        with self.app.app_context(), unittest.mock.patch(
            "flask.request", unittest.mock.Mock(headers={"Authorization": "abc"})
        ):
            self.assertRaises(self.FakeError, self.jwt.pre_request_callback)

    def test_pre_request_callback(self):
        with self.app.app_context(), unittest.mock.patch.object(
            self.jwt, "decode", lambda x, _: {"thing": x}
        ), unittest.mock.patch(
            "flask.request", unittest.mock.Mock(headers={"Authorization": "Bearer abc"})
        ):
            self.jwt.pre_request_callback()
            self.assertEqual(self.jwt.current_token(), {"thing": "abc"})

    def test_registers_post(self):
        self.assertTrue(
            self.jwt.post_request_callback in self.app.after_request_funcs[None],
            f"{self.jwt.post_request_callback} not in {self.app.after_request_funcs}",
        )

    def test_post_request_callback(self):
        self.jwt.auto_update = False
        response = flask.Response()
        with self.app.app_context():
            self.assertEqual(self.jwt.post_request_callback(response), response)

    def test_post_request_callback_auto_update_with_null_token(self):
        with self.app.app_context():
            response = self.jwt.post_request_callback(flask.Response())
            self.assertTrue(self.jwt.header_key not in response.headers)

    def test_post_request_callback_auto_update(self):
        with self.app.app_context(), unittest.mock.patch.object(
            self.jwt, "encode", lambda x: "I am a token"
        ):
            self.jwt.store.set({"thing": True})
            response = self.jwt.post_request_callback(flask.Response())

        self.assertEqual(
            response.headers.get(self.jwt.header_key, None),
            f"{self.jwt.token_prefix}I am a token",
        )
