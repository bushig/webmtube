# _*_ coding:utf-8 _*_
import atexit

import falcon
from falcon_cors import CORS

from views import ScreamerResource
from models import Base, engine
from middleware import RequireJSON, JSONTranslator
from utils import before_shutdown_handler

# Init DB
Base.metadata.create_all(engine)

cors = CORS(allow_all_origins=True, allow_all_headers=True, allow_all_methods=True)

# Callable WSGI app
app = falcon.API(middleware=[cors.middleware, RequireJSON(), JSONTranslator()])

# Resources for API
screamer_resource = ScreamerResource()

# Routing
app.add_route('/check', screamer_resource)

atexit.register(before_shutdown_handler)
