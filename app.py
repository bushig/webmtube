# _*_ coding:utf-8 _*_
import falcon
from falcon_cors import CORS

from views import ScreamerResource
from models import Base, engine
from middleware import RequireJSON, JSONTranslator

# Init DB
Base.metadata.create_all(engine)

cors = CORS(allow_all_origins=True, allow_all_headers=True, allow_all_methods=True)

# Callable WSGI app
app = falcon.API(middleware=[cors.middleware, RequireJSON(), JSONTranslator()])

# Resources for API
screamer_resource = ScreamerResource()

# Routing
app.add_route('/check', screamer_resource)

# if __name__ == '__main__':
#     httpd = simple_server.make_server('127.0.0.1', 8000, app)
#     httpd.serve_forever() #--- Starting wsgi app on Windows
