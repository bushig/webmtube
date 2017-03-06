import json

import falcon
import redis
from falcon import status_codes

from models import Session, WEBM
from utils import is_valid_2ch_url
from tasks import analyse_video
from caching import set_cache_delayed, get_cache, set_cache

r = redis.StrictRedis(host='localhost', port=6379, db=1)


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
        webm_redis_info = get_cache(md5)  # info from redis
        print("Data from redis: ", webm_redis_info)
        webm = None
        # If no data in redis store, get it from DB
        if webm_redis_info is None:
            session = Session()
            webm = session.query(WEBM).get(md5)
        # If webm was in DB, return it
        if webm:
            DB_data = webm.to_dict()
            request.context['result'] = DB_data
            set_cache(DB_data)
        else:
            if webm_redis_info == "delayed":
                response.status = status_codes.HTTP_202
                request.context['result'] = {"md5": md5, "message": "Уже анализируется"}
            elif is_valid_2ch_url(url) and webm_redis_info is None:
                analyse_video.delay(md5, url)
                set_cache_delayed(md5)
                print('Added task')
                response.status = status_codes.HTTP_202
                request.context['result'] = {"md5": md5, "message": "Добавлено в очередь на анализ"}
            else:
                # not valid url
                response.status = status_codes.HTTP_400
                request.context['result'] = {"md5": md5,
                                             "message": "Неправильный запрос"}


    def on_post(self, request, response):
        webm_list = request.context['doc']
        response.set_header("Access-Control-Allow-Origin", "*")
        resp_data = []
        try:
            for webm in webm_list:
                md5 = webm["md5"]
                url = webm["url"]
                webm_response = None
                webm_from_db = None

                webm_redis_info = get_cache(md5)

                if webm_redis_info is None:
                    session = Session()  # TODO: make one session instance
                    webm_from_db = session.query(WEBM).get(md5)
                # If webm was in DB, return it
                if webm_from_db:
                    DB_data = webm_from_db.to_dict()
                    webm_response = DB_data
                    set_cache(DB_data)
                else:
                    if webm_redis_info == "delayed":
                        webm_response = {"md5": md5, "message": "Уже анализируется"}
                    elif is_valid_2ch_url(url) and webm_redis_info is None:
                        analyse_video.delay(md5, url)
                        set_cache_delayed(md5)
                        print('Added task')
                        webm_response = {"md5": md5, "message": "Добавлено в очередь на анализ"}
                    else:
                        webm_response = {"md5": md5, "message": "Неправильный url"}

                resp_data.append(webm_response)
            # response.status = status_codes.HTTP_200
            request.context['result'] = resp_data
            # print(response.body)


        except Exception as e:
            response.status = status_codes.HTTP_400
            request.context['result'] = {"message": "Неправильный запрос"}
            print("error:", e)
