# _*_ coding:utf-8 _*_

import falcon
from falcon_cors import CORS

from webmtube.middleware import RequireJSON, JSONTranslator
from webmtube.models import Base, engine
from webmtube.views import ScreamerResource, ViewWEBMResource, LikeResource, DislikeResource

# Init DB
Base.metadata.create_all(engine)

# Logging init
# LOGGING_FALCON_PATH = os.path.join(LOGGING_PATH, LOGGING_FALCON_FILE)
# LOGGING_CELERY_PATH = os.path.join(LOGGING_PATH, LOGGING_CELERY_FILE)
# if not os.path.exists(LOGGING_PATH):
#     os.makedirs(LOGGING_PATH)
#     open(LOGGING_FALCON_PATH, 'a').close()
#     open(LOGGING_CELERY_FILE, 'a').close()
#
# log = logging.getLogger('falcon')
# log.setLevel(LOG_LEVEL)
# formatter = logging.Formatter('%(asctime)s [%(pathname)s:%(lineno)d] %(levelname)8s: %(message)s')
# handler = TimedRotatingFileHandler(LOGGING_FALCON_PATH, when='d', interval=1, backupCount=35)
# handler.setFormatter(formatter)
# log.addHandler(handler)
#
# log = logging.getLogger('celery')
# log.setLevel(LOG_LEVEL)
# formatter = logging.Formatter('%(asctime)s::%(message)s')
# handler = TimedRotatingFileHandler(LOGGING_CELERY_PATH, when='d', interval=1, backupCount=35)
# handler.setFormatter(formatter)
# log.addHandler(handler)

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