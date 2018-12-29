from typing import List, Tuple, Union

import flask

from . import jwt, route, schema


class App(flask.Flask):
    def __init__(self, *args, **kwargs):
        self.jwt_handler = jwt.JwtHandler()
        super(App, self).__init__(*args, **kwargs)

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
