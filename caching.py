import redis
from models import Session, WEBM

r = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)


def set_cache(webm_data):
    """
    :param webm_data: dict with data from DB
    :return: True when successful and False otherwise
    """
    md5 = webm_data.get('md5', None)  # TODO: check its schema
    if md5:
        r_type = r.type(md5)
        if r_type == 'none':
            r.hmset(md5, webm_data)
            r.rpush('webmlist', md5)
            return True
    return False


def set_cache_delayed(md5):
    r.set(md5, 'delayed')


def del_cache(md5):
    r.delete(md5)


def pop_webm_from_redis_list():
    return r.lpop('webmlist')


def save_webm_to_db(md5):
    data = r.hgetall(md5)
    session = Session()
    webm = session.query(WEBM).get(md5)
    webm.views = data['views']
    webm.likes = data['likes']
    webm.dislikes = data['dislikes']
    session.commit()  # TODO: maybe should be one bulk operation to save all webms
    del_cache(md5)


def get_cache(md5):
    """
    :return: WEBM data, 'delayed' message or None depending on results
    """
    r_type = r.type(md5)

    if r_type == 'hash':
        cache = r.hgetall(md5)
        if cache.get('screamer_chance', None) == 'None':  # Because of redis-py (nil) value casting
            cache['screamer_chance'] = None
        return cache
    elif r_type == 'string':
        return 'delayed'  # TODO: maybe get this value from redis storage
    else:
        return


def incr_views(md5):
    """
    :return: True if increased, False if failed
    """
    try:
        r.hincrby(md5, 'views')
        return True
    except Exception as e:
        return False
