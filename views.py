import falcon


class ScreamerResource:
    """Used to check one WEBM"""

    def on_get(self, request, response):
        response.status = falcon.HTTP_200
        response.body = ('Hello world')
