import flask_testing
from flask import Blueprint, Config, Flask

from flapi.jwt import HasScopes, JwtHandler, MatchValue, protect

blueprint = Blueprint("test_blueprint", __name__)
jwt_handler = JwtHandler()


class ApiConfig(Config):
    JWT_SECRET = "secret"
    JWT_LIFESPAN = 10
    JWT_ALGORITHM = "HS256"
    JWT_AUTO_UPDATE = True


@blueprint.route("/token", methods=["GET"])
def get_token():
    print("/token")
    jwt_handler.generate_token({"uuid": "123"}, ["read:protected"])
    return "success"


@blueprint.route("/protected", methods=["GET"])
@protect(HasScopes("read:protected"))
def protected():
    print("/protected")
    return "success"


@blueprint.route("/protected/<uuid>", methods=["GET"])
@protect(HasScopes("read:protected"), MatchValue("jwt:uuid", "url:uuid"))
def protected_user(uuid):
    print(f"/protected/{uuid}")
    return uuid


class TestApi(flask_testing.TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config.from_object(ApiConfig)
        app.register_blueprint(blueprint)
        jwt_handler.init_app(app)
        return app

    def test_run(self):

        auth_key = "Authorization"
        self.assert500(self.client.get("/protected"))
        self.assert500(self.client.get("/protected/123"))

        token_response = self.client.get("/token")
        self.assert200(token_response)
        token = token_response.headers.get(auth_key, None)
        self.assertIsNotNone(token)

        protected_response = self.client.get("/protected", headers={auth_key: token})
        self.assert200(protected_response)
        token = protected_response.headers.get(auth_key, None)
        self.assertIsNotNone(token)

        protected_user_response = self.client.get(
            "/protected/123", headers={auth_key: token}
        )
        self.assert200(protected_user_response)
        token = protected_user_response.headers.get(auth_key, None)
        self.assertIsNotNone(token)

        protected_user_response = self.client.get(
            "/protected/321", headers={auth_key: token}
        )
        self.assert500(protected_user_response)
