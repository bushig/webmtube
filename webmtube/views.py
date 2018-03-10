import logging

from falcon import status_codes

from webmtube.caching import set_cache_delayed, get_cache, set_cache, incr_views, like_webm, check_ip_viewed
from webmtube.tasks import analyse_video
from webmtube.utils import is_valid_2ch_url

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
        md5 = request.get_param('md5')
        url = request.get_param('url')
        response.set_header("Access-Control-Allow-Origin", "*")
        webm_redis_info = get_cache(md5)  # data, delayed or None
        # print("redis:", webm_redis_info)
        # If data in cache
        if isinstance(webm_redis_info, dict):
            webm_redis_info['md5'] = md5
            response.status = status_codes.HTTP_200
            request.context['result'] = webm_redis_info
        # If webm is analysed
        elif webm_redis_info == "delayed":
            response.status = status_codes.HTTP_202
            request.context['result'] = {"md5": md5, "message": "Уже анализируется"}
        # If no cache data
        elif webm_redis_info is None:
            if is_valid_2ch_url(url):
                analyse_video.delay(md5, url)
                set_cache_delayed(md5)
                response.status = status_codes.HTTP_202
                request.context['result'] = {"md5": md5, "message": "Добавлено в очередь на анализ"}
            else:
                # not valid url
                response.status = status_codes.HTTP_400
                request.context['result'] = {"md5": md5,
                                             "message": "Неправильная ссылка в запросе"}
        else:
            response.status = status_codes.HTTP_502
            request.context['result'] = {"md5": md5,
                                         "message": "Some error"}

    def on_post(self, request, response):
        webm_list = request.context['doc']
        resp_data = []
        try:
            for webm in webm_list:
                md5 = webm["md5"]
                url = webm["url"]
                webm_response = None

                webm_redis_info = get_cache(md5)  # clean_md5, delayed or None
                if isinstance(webm_redis_info, dict):
                    webm_redis_info['md5'] = md5
                    webm_response = webm_redis_info
                elif webm_redis_info == "delayed":
                    webm_response = {"md5": md5, "message": "Уже анализируется"}
                elif webm_redis_info is None:
                    if is_valid_2ch_url(url):
                        analyse_video.delay(md5, url)
                        set_cache_delayed(md5)
                        webm_response = {"md5": md5, "message": "Добавлено в очередь на анализ"}
                    else:
                        webm_response = {"md5": md5, "message": "Неправильный url"}
                else:
                    webm_response = {"md5": md5, "message": "Some error"}

                resp_data.append(webm_response)
            request.context['result'] = resp_data


        except Exception as e:
            response.status = status_codes.HTTP_400
            request.context['result'] = {"message": "Неправильный запрос"}
            print("error in post request:", e)


class ViewWEBMResource:
    def on_post(self, request, response, md5):
        # ip = request.access_route[-1]
        ip = '127.0.0.1'
        # viewed = check_ip_viewed(md5, ip)
        viewed = ''
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
        # print(request.access_route)
        # ip = request.access_route[-1]
        ip = '127.0.0.1'
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
        # ip = request.access_route[-1]
        ip = '127.0.0.1'
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
