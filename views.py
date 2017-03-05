import json

import falcon
import redis
from falcon import status_codes

from models import Session, WEBM
from utils import is_valid_2ch_url
from tasks import analyse_video

r = redis.StrictRedis(host='localhost', port=6379, db=1)


class JsonOnlyMiddleware:
    def process_request(self, request, response):
        if request.method == 'POST' and 'application/json' not in request.content_type:
            raise falcon.HTTPUnsupportedMediaType('This API only supports requests encoded as JSON.')


class ScreamerResource:
    """
    Used to check one WEBM.
    If already checked, return code 200 and WEBM info.
    If not checked return code 202.j
    """

    # TODO: Short WEBM returns null scream chance all the time, fix it
    # TODO: If in DB return result, if not in DB, return message that added to analyze, if wrong url throw error

    def on_get(self, request, response):
        print(request.get_param_as_list('url'))
        md5 = request.get_param('md5')
        url = request.get_param('url')
        response.set_header("Access-Control-Allow-Origin", "*")
        webm_redis_info = r.get(md5)  # info from redis
        print("Data from redis: ", webm_redis_info)
        webm = None
        # If no data in redis store, get it from DB
        if webm_redis_info is None:
            session = Session()
            webm = session.query(WEBM).get(md5)
        else:
            webm_redis_info = webm_redis_info.decode("utf-8")
        # If webm was in DB, return it
        if webm:
            dump = json.dumps(webm.to_dict(), indent=4)
            response.body = dump
        else:
            if webm_redis_info == "delayed":
                response.status = status_codes.HTTP_202
                response.body = json.dumps({"md5": md5, "message": "Уже анализируется"})
            elif is_valid_2ch_url(url) and webm_redis_info is None:
                analyse_video.delay(md5, url)
                r.set(md5, 'delayed')
                print('Added task')
                response.status = status_codes.HTTP_202
                response.body = json.dumps({"md5": md5, "message": "Добавлено в очередь на анализ"})
            else:
                # not valid url
                response.status = status_codes.HTTP_400
                response.body = json.dumps({"md5": md5,
                                            "message": "Неправильный запрос"})  # TODO: Make error handling with JSON(error attrbute)

                # TODO Add CheckJSON middleware to allow only JSON reqs and resps

    def on_post(self, request, response):
        data = request.stream.read(request.content_length or 0).decode('utf-8')
        response.set_header("Access-Control-Allow-Origin", "*")
        resp_data = []
        try:
            webm_list = json.loads(data)
            for webm in webm_list:
                md5 = webm["md5"]
                url = webm["url"]
                webm_response = None
                webm_from_db = None

                webm_redis_info = r.get(md5)

                if webm_redis_info is None:
                    session = Session()  # TODO: make one session instance
                    webm_from_db = session.query(WEBM).get(md5)
                else:
                    webm_redis_info = webm_redis_info.decode("utf-8")
                # If webm was in DB, return it
                if webm_from_db:
                    webm_response = webm_from_db.to_dict()
                else:
                    if webm_redis_info == "delayed":
                        webm_response = {"md5": md5, "message": "Уже анализируется"}
                    elif is_valid_2ch_url(url) and webm_redis_info is None:
                        analyse_video.delay(md5, url)
                        r.set(md5, 'delayed')
                        print('Added task')
                        webm_response = {"md5": md5, "message": "Добавлено в очередь на анализ"}
                    else:
                        webm_response = {"md5": md5, "message": "Неправильный url"}

                resp_data.append(webm_response)
            response.status = status_codes.HTTP_200
            response.body = json.dumps(resp_data)
            # print(response.body)


        except Exception as e:
            response.status = status_codes.HTTP_400
            response.body = {"message": "Неправильный запрос"}
            print("error:", e)
