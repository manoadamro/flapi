from typing import List, Tuple, Union

import flask

from . import jwt, route, schema


class App(flask.Flask):
    def __init__(self, *args, jwt_handler=None, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.jwt_handler = self._create_jwt_handler(jwt_handler)

    def _create_jwt_handler(self, jwt_handler):
        if jwt_handler is True:
            return jwt.JwtHandler(app=self)
        if jwt_handler is not None:
            jwt_handler.init_app(self)
            return jwt_handler
        return jwt_handler

    def route(
        self,
        rule,
        json: Union[schema.Schema] = None,
        auth: Union[jwt.JWTRule, List, Tuple] = None,
        **options
    ):
        return route.Route(
            super(App, self).route(rule, **options), json=json, auth=auth
        )


class Blueprint(flask.Flask):
    def route(
        self,
        rule,
        json: Union[schema.Schema] = None,
        auth: Union[jwt.JWTRule, List, Tuple] = None,
        **options
    ):
        return route.Route(
            super(Blueprint, self).route(rule, **options), json=json, auth=auth
        )
