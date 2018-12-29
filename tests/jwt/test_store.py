import unittest
import unittest.mock
import flask

from flapi.jwt.store import Store


class JWTStoreTest(unittest.TestCase):

    fake_g = {"some": "thing", "other": True}

    def setUp(self):
        self.store = Store

    @unittest.mock.patch.object(flask, "g", unittest.mock.Mock())
    def test_sets_g_object(self):
        self.store.set(self.fake_g)
        self.assertTrue(hasattr(flask.g, Store.key))

    @unittest.mock.patch.object(flask, "g", unittest.mock.Mock())
    def test_sets_object(self):
        self.store.set(self.fake_g)
        self.assertEqual(self.fake_g, flask.g.jwt)

    @unittest.mock.patch.object(flask, "g", unittest.mock.Mock())
    def test_gets_object(self):
        self.store.set(self.fake_g)
        token = self.store.get()
        self.assertEqual(self.fake_g, token)

    @unittest.mock.patch.object(flask, "g", unittest.mock.Mock(spec=fake_g))
    def test_returns_none_if_no_token_set(self):
        self.assertIsNone(self.store.get())
