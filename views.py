import json

import falcon

from models import Session, WEBM
from scream_detector import detect_scream

class ScreamerResource:
    """Used to check one WEBM"""

    # TODO: If in DB return result, if not in DB, return message that added to analyze, if wrong url throw error
    def on_get(self, request, response):
        session = Session()
        md5 = request.get_param('md5', required=True)
        url = request.get_param('url')

        webm = session.query(WEBM).get(md5)
        print("WEBM {}".format(webm))
        if webm:
            response.status = falcon.HTTP_200
            response.body = ('Hello world {}'.format(webm))
        else:
            webm = detect_scream(md5, url)
            response.body = "Added WEBM {}".format(webm)
