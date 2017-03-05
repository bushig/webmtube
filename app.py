# _*_ coding:utf-8 _*_
import falcon
# from wsgiref import simple_server
from views import ScreamerResource, JsonOnlyMiddleware
from models import Base, engine

# Init DB
Base.metadata.create_all(engine)

# Callable WSGI app
app = falcon.API(middleware=[JsonOnlyMiddleware()])

# Resources for API
screamer_resource = ScreamerResource()

# Routing
app.add_route('/check', screamer_resource)

# if __name__ == '__main__':
#     httpd = simple_server.make_server('127.0.0.1', 8000, app)
#     httpd.serve_forever() #--- Starting wsgi app on Windows
