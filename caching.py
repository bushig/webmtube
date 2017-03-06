import redis

r = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)


def set_cache(webm_data):
    """
    :param webm_data: dict with data from DB
    :return: True when successful and False otherwise
    """
    md5 = webm_data.pop('md5', None)
    if md5:
        if r.type(md5) == 'hash':
            r.hmset(md5, webm_data)
            return True
    return False


def set_cache_delayed(md5):
    r.set(md5, 'delayed')


def del_cache(md5):
    r.delete(md5)


def get_cache(md5):
    """
    :return: WEBM data, 'delayed' message or None depending on results
    """
    r_type = r.type(md5)

    if r_type == 'hash':
        return r.hgetall(md5)
    elif r_type == 'string':
        return 'delayed'  # TODO: maybe get value from redis storage
    else:
        return
