import json

import falcon
from falcon import status_codes

from models import Session, WEBM
from utils import is_valid_2ch_url
from tasks import analyse_video

class ScreamerResource:
    """
    Used to check one WEBM.
    If already checked, return code 200 and WEBM info.
    If not checked return code 202.j
    """

    # TODO: Short WEBM returns null scream chance all the time, fix it
    # TODO: If in DB return result, if not in DB, return message that added to analyze, if wrong url throw error
    def on_get(self, request, response):
        session = Session()
        print(request.get_param_as_list('url'))
        md5 = request.get_param('md5')
        url = request.get_param('url')
        response.set_header("Access-Control-Allow-Origin", "*")
        webm = session.query(WEBM).get(md5)
        if webm:
            dump = json.dumps(webm.to_dict(), indent=4)
            response.body = dump
        else:
            if is_valid_2ch_url(url):
                analyse_video.delay(md5, url)
                response.status = status_codes.HTTP_202
                response.body = ""
            else:
                response.status = status_codes.HTTP_400
                response.body = 'Not valid url in request'  # TODO: Make error handling with JSON(error attrbute)

            # TODO Add CheckJSON middleware to allow only JSON reqs and resps
