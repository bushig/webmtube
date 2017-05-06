# _*_ coding:utf-8 _*_

import falcon
from falcon_cors import CORS
from sqlalchemy import create_engine

from webmtube import Session
from webmtube.middleware import RequireJSON, JSONTranslator
from webmtube.models import Base
from webmtube.views import ScreamerResource, ViewWEBMResource, LikeResource, DislikeResource

from webmtube.config import DB_ENGINE


def create_app(database_uri):
    # Init DB
    engine = create_engine(database_uri)
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)
    cors = CORS(allow_all_origins=True, allow_all_headers=True, allow_all_methods=True)

    # Resources for API
    screamer_resource = ScreamerResource()
    view_webm_resource = ViewWEBMResource()
    like_resource = LikeResource()
    dislike_resource = DislikeResource()

    # Callable WSGI app
    app = falcon.API(middleware=[cors.middleware, RequireJSON(), JSONTranslator()])

    # Routing
    app.add_route('/check', screamer_resource)
    app.add_route('/check/{md5}/view', view_webm_resource)
    app.add_route('/check/{md5}/like', like_resource)
    app.add_route('/check/{md5}/dislike', dislike_resource)

    return app


# Production app
def get_app():
    return create_app(DB_ENGINE)
