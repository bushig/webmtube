import logging

import redis
from falcon import status_codes

from webmtube.caching import set_cache_delayed, get_cache, set_cache, incr_views, like_webm, check_ip_viewed
from webmtube.models import Session, WEBM
from webmtube.tasks import analyse_video
from webmtube.utils import is_valid_2ch_url

r = redis.StrictRedis(host='localhost', port=6379, db=1)
falcon_log = logging.getLogger('falcon')


class ScreamerResource:
    """
    Used to check one WEBM.
    If already checked, return code 200 and WEBM info.
    If not checked return code 202.
    """

    # TODO: Short WEBM returns null scream chance all the time, fix it
    # TODO: If in DB return result, if not in DB, return message that added to analyze, if wrong url throw error

    def on_get(self, request, response):
        falcon_log.info('Received GET request with params {}, trying to acquire data from Redis'.format(
            request.get_param_as_list('url')))
        # print(request.get_param_as_list('url'))
        md5 = request.get_param('md5')
        url = request.get_param('url')
        response.set_header("Access-Control-Allow-Origin", "*")
        # print("Data from redis: ", webm_redis_info)
        webm_redis_info = get_cache(md5)  # info from redis
        falcon_log.info('Data from redis: {}'.format(webm_redis_info))
        webm = None
        # If no data in redis store, get it from DB
        if webm_redis_info is None:
            falcon_log.info('Getting data from DB')
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
            elif isinstance(webm_redis_info, dict):
                response.status = status_codes.HTTP_200
                request.context['result'] = webm_redis_info
            elif is_valid_2ch_url(url) and webm_redis_info is None:
                analyse_video.delay(md5, url)
                falcon_log.info('Adding WEBM to task queue with url of {}'.format(url))
                set_cache_delayed(md5)
                # print('Added task')
                response.status = status_codes.HTTP_202
                request.context['result'] = {"md5": md5, "message": "Добавлено в очередь на анализ"}
            else:
                # not valid url
                response.status = status_codes.HTTP_400
                request.context['result'] = {"md5": md5,
                                             "message": "Неправильный запрос"}

    def on_post(self, request, response):
        falcon_log.info('Received POST request with params {}, trying to acquire data from Redis'.format(
            request.context['doc']))
        webm_list = request.context['doc']
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
                    elif isinstance(webm_redis_info, dict):
                        webm_response = webm_redis_info
                    elif is_valid_2ch_url(url) and webm_redis_info is None:
                        analyse_video.delay(md5, url)
                        falcon_log.info('Adding WEBM to task queue with url of {}'.format(url))
                        set_cache_delayed(md5)
                        # print('Added task')
                        webm_response = {"md5": md5, "message": "Добавлено в очередь на анализ"}
                    else:
                        webm_response = {"md5": md5, "message": "Неправильный url"}

                resp_data.append(webm_response)
            request.context['result'] = resp_data


        except Exception as e:
            response.status = status_codes.HTTP_400
            request.context['result'] = {"message": "Неправильный запрос"}
            print("error in post request:", e)


class ViewWEBMResource:
    def on_post(self, request, response, md5):
        ip = request.access_route[-1]
        viewed = check_ip_viewed(md5, ip)
        if type(viewed) == int:
            print('Until views reset: ', viewed)
            response.status = status_codes.HTTP_304
            request.context['result'] = {"ttl": viewed}  # in seconds
        else:
            succeed = incr_views(ip, md5)
            if succeed:
                response.status = status_codes.HTTP_200
            else:
                response.status = status_codes.HTTP_409
                request.context['result'] = {"message": "Ошибка"}  # TODO: make NO WEBM IN REDIS error


class LikeResource:
    def on_post(self, request, response, md5):
        ip = request.access_route[
            -1]  # TODO: IP можно подделать в хедере + могут иногда быть значения unknown и obfuscated
        # Возможно сделать валидацию и, на всякий случай, исключить локалхост
        print('Like from ip: ', ip)
        data = like_webm(md5, ip, 'like')
        if data:
            response.status = status_codes.HTTP_200
            request.context['result'] = data
        else:
            response.status = status_codes.HTTP_409
            request.context['result'] = {"message": "Нет такой WEBM в кэше"}


class DislikeResource:
    def on_post(self, request, response, md5):
        ip = request.access_route[-1]
        print('Dislike from ip: ', ip)
        data = like_webm(md5, ip, 'dislike')
        if data:
            response.status = status_codes.HTTP_200
            request.context['result'] = data
        else:
            response.status = status_codes.HTTP_409
            request.context['result'] = {"message": "Нет такой WEBM в кэше"}

# class GetLikesResource:
#     # TODO: Взять для всех мд5 информацию о том лайкал он или нет. На фронте кэшировать чтобы не делать лишние запросы.
#     def on_post:
#         pass
