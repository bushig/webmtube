# _*_ coding:utf-8 _*_

import falcon
from falcon_cors import CORS

from webmtube.middleware import RequireJSON, JSONTranslator
from webmtube.models import Base, engine
from webmtube.views import ScreamerResource, ViewWEBMResource, LikeResource, DislikeResource

# Init DB
Base.metadata.create_all(engine)

cors = CORS(allow_all_origins=True, allow_all_headers=True, allow_all_methods=True)

# Callable WSGI app
app = falcon.API(middleware=[cors.middleware, RequireJSON(), JSONTranslator()])

# Resources for API
screamer_resource = ScreamerResource()
view_webm_resource = ViewWEBMResource()
like_resource = LikeResource()
dislike_resource = DislikeResource()

# TODO: To get user real ip reconfigure nginix according to http://docs.gunicorn.org/en/stable/deploy.html (set X-Forwarded-For header)
# Routing
app.add_route('/check', screamer_resource)
app.add_route('/check/{md5}/view', view_webm_resource)
app.add_route('/check/{md5}/like', like_resource)
app.add_route('/check/{md5}/dislike', dislike_resource)
