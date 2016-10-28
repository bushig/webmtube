import falcon

from views import ScreamerResource
from models import Base, engine

# Init DB
Base.metadata.create_all(engine)

# Callable WSGI app
app = falcon.API()

# Resources for API
screamer_resource = ScreamerResource()

# Routing
app.add_route('/check', screamer_resource)
