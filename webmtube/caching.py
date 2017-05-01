import redis

from webmtube.models import Session, WEBM

r = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)


def set_cache(webm_data):
    """
    :param webm_data: dict with data from DB
    :return: True when successful and False otherwise
    """
    md5 = webm_data.get('md5', None)  # TODO: check its schema
    if md5:
        r_type = r.type('webm:' + md5)
        if r_type == 'none':
            r.hmset('webm:' + md5, webm_data)
            r.rpush('webmlist', md5)
            return True
    return False


def set_cache_delayed(md5):
    r.set('webm:' + md5, 'delayed')


def del_cache(md5):
    r.delete('webm:' + md5)


def del_all_cache():
    """Delete all cache in WEBM: namespace"""
    for key in r.scan_iter("webm:*"):
        print('deleted: {}'.format(key))
        r.delete(key)


def pop_webm_from_redis_list():
    return r.lpop('webmlist')


def save_webm_to_db(md5):
    r_type = r.type('webm:' + md5)

    if r_type == 'hash':
        data = r.hgetall('webm:' + md5)
        session = Session()
        webm = session.query(WEBM).get(md5)
        webm.views = data['views']
        webm.likes = data['likes']
        webm.dislikes = data['dislikes']
        session.commit()  # TODO: maybe should be one bulk operation to save all webms
    else:
        print('Not hash')
    del_cache(md5)


def get_cache(md5):
    """
    :return: WEBM data, 'delayed' message or None depending on results
    """
    r_type = r.type('webm:' + md5)

    if r_type == 'hash':
        cache = r.hgetall('webm:' + md5)
        if cache.get('screamer_chance', None) == 'None':  # Because of redis-py (nil) value casting
            cache['screamer_chance'] = None
        return cache
    elif r_type == 'string':
        return 'delayed'  # TODO: maybe get this value from redis storage
    else:
        return


def incr_views(ip, md5):
    """
    :return: True if increased, False if failed
    """
    r_type = r.type('webm:' + md5)
    print(md5, r_type)  # TODO: Если нет в кэше, загрузить и увеличить счетчик.
    if r_type == 'hash':
        r.hincrby('webm:' + md5, 'views')
        r.setex("views:{}:{}".format(ip, md5), 600, 'v')
        return True
    return False


def check_ip_viewed(md5, ip):
    """
    return TTL of key if viewed and return False is expired or didnt viewed
    """
    ttl = r.ttl("views:{}:{}".format(ip, md5))
    if ttl == -2:  # expired
        return False
    else:
        return ttl


def like_webm(md5, ip, action):
    # Если все прошло удачно - вернуть словарь с количеством лайков/дизлайков, иначе вернуть None
    # в ip:127.0.0.1 хранится хэш вида {viewed:{ISO TIME} action:{nil, like or dislike}}
    r_type = r.type('webm:' + md5)
    if r_type == 'hash':
        ip_action = r.hget('ip:' + ip + ":" + md5, 'action')
        # Убираем лайк
        if action == ip_action:
            r.hincrby('webm:' + md5, action + 's', -1)
            r.hset('ip:' + ip + ":" + md5, 'action', None)
            action = None
        # Спокойно ставим лайк
        elif ip_action is None:
            r.hincrby('webm:' + md5, action + 's')
            r.hset('ip:' + ip + ":" + md5, 'action', action)
        # Убираем одно действие и ставим другое
        else:
            r.hincrby('webm:' + md5, action + 's')
            r.hincrby('webm:' + md5, ip_action + 's', -1)
            r.hset('ip:' + ip + ":" + md5, 'action', action)
        result = r.hmget('webm:' + md5, ('likes', 'dislikes'))
        return {'md5': md5, 'likes': result[0], 'dislikes': result[1], 'action': action}
    return