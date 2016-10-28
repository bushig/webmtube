import json

import falcon
from falcon import status_codes

from models import Session, WEBM
from scream_detector import analyse_video


class ScreamerResource:
    """
    Used to check one WEBM.
    If already checked, return code 200 and WEBM info.
    If not checked return code 202.j
    """

    # TODO: If in DB return result, if not in DB, return message that added to analyze, if wrong url throw error
    def on_get(self, request, response):
        session = Session()
        md5 = request.get_param('md5')
        url = request.get_param('url')

        webm = session.query(WEBM).get(md5)
        if webm:
            dump = json.dumps(webm.to_dict(), indent=4)
            response.body = dump
        else:
            analyse_video(md5, url)
            response.status = status_codes.HTTP_202

            # TODO Add CheckJSON middleware to allow only JSON reqs and resps
