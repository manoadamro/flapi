import unittest
import unittest.mock

import flask
import jwt as pyjwt

from flapi.jwt.app import JwtHandler


class JwtTest(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)
        self.handler = JwtHandler(self.app)
        self.handler.secret = "secret"
        self.handler.lifespan = 300
        self.handler.validation_error = self.FakeError

    @property
    def jwt(self):
        return {"some": "thing"}

    @property
    def scopes(self):
        return "read:thing", "write:thing"

    class FakeError(pyjwt.PyJWTError):
        pass

    def test_registers_pre(self):
        self.assertTrue(
            self.handler.before_request in self.app.before_request_funcs[None],
            f"{self.handler.before_request} not in {self.app.before_request_funcs}",
        )

    def test_pre_request_callback_null_token(self):
        with self.app.app_context(), unittest.mock.patch(
            "flask.request", unittest.mock.Mock(headers={})
        ):
            self.handler.before_request()
            self.assertIsNone(self.handler._store.get())

    def test_pre_request_callback_invalid_token(self):
        with self.app.app_context(), unittest.mock.patch(
            "flask.request", unittest.mock.Mock(headers={"Authorization": "abc"})
        ):
            self.assertRaises(self.FakeError, self.handler.before_request)

    def test_pre_request_callback(self):
        with self.app.app_context(), unittest.mock.patch.object(
            self.handler, "_decode", lambda x: {"thing": x}
        ), unittest.mock.patch(
            "flask.request", unittest.mock.Mock(headers={"Authorization": "Bearer abc"})
        ):
            self.handler.before_request()
            self.assertEqual(self.handler.current_token(), {"thing": "abc"})

    def test_registers_post(self):
        self.assertTrue(
            self.handler.after_request in self.app.after_request_funcs[None],
            f"{self.handler.after_request} not in {self.app.after_request_funcs}",
        )

    def test_post_request_callback(self):
        self.handler.app.config["JWT_AUTO_UPDATE"] = False
        response = flask.Response()
        with self.app.app_context():
            self.assertEqual(self.handler.after_request(response), response)

    def test_post_request_callback_auto_update_with_null_token(self):
        with self.app.app_context():
            response = self.handler.after_request(flask.Response())
            self.assertTrue(self.handler.header_key not in response.headers)

    def test_post_request_callback_auto_update(self):
        with self.app.app_context(), unittest.mock.patch.object(
            self.handler, "_encode", lambda x: "I am a token"
        ):
            self.handler.app.config["JWT_AUTO_UPDATE"] = True
            self.handler._store.set({"thing": True})
            response = self.handler.after_request(flask.Response())

        self.assertEqual(
            response.headers.get(self.handler.header_key, None),
            f"{self.handler.token_prefix}I am a token",
        )

    def test_current_token(self):
        expected = {"some": "thing"}
        with unittest.mock.patch.object(self.handler._store, "get", lambda: expected):
            token = self.handler.current_token()
        self.assertEqual(token, expected)

    def test_null_current_token(self):
        with unittest.mock.patch.object(self.handler._store, "get", lambda: None):
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
