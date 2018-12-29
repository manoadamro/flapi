import unittest
import unittest.mock

import flask

from flapi.jwt.rules import MatchValue


class MatchValueTest(unittest.TestCase):
    def test_invalid_object(self):
        paths = "nope:uuid", "jwt:uuid"
        self.assertRaises(AttributeError, MatchValue, *paths)

    def test_single_path(self):
        path = "jwt:uuid"
        self.assertRaises(ValueError, MatchValue, path)

    def test_header(self):
        paths = "header:uuid", "jwt:uuid"
        header = {"uuid": "1234"}
        token = {"uuid": "1234"}
        rule = MatchValue(*paths)
        with unittest.mock.patch.object(
            flask, "request", unittest.mock.Mock(headers=header)
        ):
            self.assertTrue(rule(token))

    def test_header_fails(self):
        paths = "header:uuid", "jwt:uuid"
        header = {"uuid": "1234"}
        token = {"uuid": "4321"}
        rule = MatchValue(*paths)
        with unittest.mock.patch.object(
            flask, "request", unittest.mock.Mock(headers=header)
        ):
            self.assertFalse(rule(token))

    def test_json(self):
        paths = "json:user/uuid", "jwt:uuid"
        json = {"user": {"uuid": "1234"}}
        token = {"uuid": "1234"}
        rule = MatchValue(*paths)
        with unittest.mock.patch.object(
            flask, "request", unittest.mock.Mock(json=json)
        ):
            self.assertTrue(rule(token))

    def test_json_fails(self):
        paths = "json:user/uuid", "jwt:uuid"
        json = {"user": {"uuid": "4321"}}
        token = {"uuid": "1234"}
        rule = MatchValue(*paths)
        with unittest.mock.patch.object(
            flask, "request", unittest.mock.Mock(json=json)
        ):
            self.assertFalse(rule(token))

    def test_url(self):
        paths = "url:uuid", "jwt:uuid"
        view_args = {"uuid": "1234"}
        token = {"uuid": "1234"}
        rule = MatchValue(*paths)
        with unittest.mock.patch.object(
            flask, "request", unittest.mock.Mock(view_args=view_args)
        ):
            self.assertTrue(rule(token))

    def test_url_fails(self):
        paths = "url:uuid", "jwt:uuid"
        view_args = {"uuid": "1234"}
        token = {"uuid": "4321"}
        rule = MatchValue(*paths)
        with unittest.mock.patch.object(
            flask, "request", unittest.mock.Mock(view_args=view_args)
        ):
            self.assertFalse(rule(token))

    def test_param(self):
        paths = "param:uuid", "jwt:uuid"
        args = {"uuid": "1234"}
        token = {"uuid": "1234"}
        rule = MatchValue(*paths)
        with unittest.mock.patch.object(
            flask, "request", unittest.mock.Mock(args=args)
        ):
            self.assertTrue(rule(token))

    def test_param_fails(self):
        paths = "param:uuid", "jwt:uuid"
        args = {"uuid": "1234"}
        token = {"uuid": "4321"}
        rule = MatchValue(*paths)
        with unittest.mock.patch.object(
            flask, "request", unittest.mock.Mock(args=args)
        ):
            self.assertFalse(rule(token))

    def test_form(self):
        paths = "form:uuid", "jwt:uuid"
        form = {"uuid": "1234"}
        token = {"uuid": "1234"}
        rule = MatchValue(*paths)
        with unittest.mock.patch.object(
            flask, "request", unittest.mock.Mock(form=form)
        ):
            self.assertTrue(rule(token))

    def test_form_fails(self):
        paths = "form:uuid", "jwt:uuid"
        form = {"uuid": "1234"}
        token = {"uuid": "4321"}
        rule = MatchValue(*paths)
        with unittest.mock.patch.object(
            flask, "request", unittest.mock.Mock(form=form)
        ):
            self.assertFalse(rule(token))
