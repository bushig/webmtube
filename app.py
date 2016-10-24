import falcon
from views import ScreamerResource

# Callable WSGI app
app = falcon.API()

# Resources for API
screamer_resource = ScreamerResource()

# Routing
app.add_route('/check', screamer_resource)
