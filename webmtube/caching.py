from webmtube.models import Session, WEBM, DirtyWEBM
from webmtube.config import CACHING_REDIS as r


def set_cache(webm_data):
    """
    :param webm_data: dict with data from DB
    :return: True when successful and False otherwise
    """
    print("setting data:", webm_data)
    id_ = webm_data.get('id', None)  # TODO: check its schema
    if id_:
        r_type = r.type('cleanwebm:' + id_)
        if r_type == 'none':
            r.hmset('cleanwebm:' + id_, webm_data)
            r.rpush('webmlist', id_)
            return True
    return False


def set_dirty_cache(md5, id_):
    r.set('dirtywebm:' + md5, id_)


def set_cache_delayed(md5):
    r.set('dirtywebm:' + md5, 'delayed')


def del_dirty_cache(md5):
    r.delete('dirtywebm:' + md5)


def del_clean_cache(id_):
    r.delete('cleanwebm:' + id_)


def del_all_dirty_cache():
    """Delete all cache in DIRTYWEBM: namespace"""
    for key in r.scan_iter("dirtywebm:*"):
        print('deleted dirty: {}'.format(key))
        r.delete(key)


def pop_webm_from_redis_list():
    return r.lpop('webmlist')


def save_webm_to_db(id_):
    r_type = r.type('cleanwebm:' + id_)

    if r_type == 'hash':
        data = r.hgetall('cleanwebm:' + id_)
        session = Session()
        webm = session.query(WEBM).get(id_)
        webm.views = data['views']
        webm.likes = data['likes']
        webm.dislikes = data['dislikes']
        session.commit()  # TODO: maybe should be one bulk operation to save all webms
        session.close()
    else:
        print('Not hash')
    del_clean_cache(id_)


def get_clean_cache(id_):
    """
    :param id_: md5 cache of stripped webm
    :return: dict with data from cache or None
    """
    r_type = r.type('cleanwebm:' + id_)

    if r_type == 'hash':
        cache = r.hgetall('cleanwebm:' + id_)
        print("clean_cachce:", cache['screamer_chance'])
        if cache.get('screamer_chance', None) == 'None':  # Because of redis-py (nil) value casting
            cache['screamer_chance'] = None
        # TODO: Convert from strings types to floats and ints
        return cache
    else:
        session = Session()
        webm_data = session.query(WEBM).get(id_)  # Assuming it will be there anyway
        set_cache(webm_data.to_dict())
        return webm_data.to_dict()


def get_dirty_cache(md5):
    """
    :return: 'delayed' message, clean_md5 or None
    """
    clean_md5 = r.get('dirtywebm:' + md5)
    return clean_md5


def get_cache(dirty_md5):
    """
    Glue between two functions - clean and dirty cache
    :param dirty_md5: original md5
    :return:  dict with data from cache, "delayed" message or None
    """
    id_ = get_dirty_cache(dirty_md5)
    print("Clean cache:", id_)
    if id_ == "delayed":
        return id_
    elif id_ is None:
        session = Session()
        dirty_data = session.query(DirtyWEBM).get(dirty_md5)
        # found id_
        if dirty_data:
            id_ = dirty_data.webm_id
            set_dirty_cache(dirty_md5, id_)
            return get_clean_cache(id_)
        # no data in dirty cache - haven't analyzed
        else:
            return
    else:
        return get_clean_cache(id_)


def incr_views(ip, md5):
    """
    :return: True if increased, False if failed
    """
    id_ = get_dirty_cache(md5)
    if id_ is not None and id_ != "delayed":
        r_type = r.type('cleanwebm:' + id_)
        print(id_, r_type)  # TODO: Если нет в кэше, загрузить и увеличить счетчик.
        if r_type == 'hash':
            r.hincrby('cleanwebm:' + id_, 'views')
            r.setex("views:{}:{}".format(ip, id_), 600, 'v')
            return True
        else:
            # Get from DB
            pass
    return False


def check_ip_viewed(md5, ip):
    """
    return TTL of key if viewed and return False is expired or didn't viewed
    """
    id_ = get_dirty_cache(md5)
    if id_ is not None and id_ != "delayed":
        ttl = r.ttl("views:{}:{}".format(ip, id_))
        if ttl == -2:  # expired
            return False
        else:
            return ttl
    return False


def like_webm(md5, ip, action):
    # Если все прошло удачно - вернуть словарь с количеством лайков/дизлайков, иначе вернуть None
    # в ip:127.0.0.1 хранится хэш вида {viewed:{ISO TIME} action:{nil, like or dislike}}
    id_ = get_dirty_cache(md5)
    if id_ is not None and id_ != "delayed":
        r_type = r.type('cleanwebm:' + id_)
        if r_type == 'hash':
            ip_action = r.hget('ip:' + ip + ":" + id_, 'action')
            # Убираем лайк
            if action == ip_action:
                r.hincrby('cleanwebm:' + id_, action + 's', -1)
                r.hset('ip:' + ip + ":" + id_, 'action', None)
                action = None
            # Спокойно ставим лайк
            elif ip_action is None:
                r.hincrby('cleanwebm:' + id_, action + 's')
                r.hset('ip:' + ip + ":" + id_, 'action', action)
            # Убираем одно действие и ставим другое
            else:
                r.hincrby('cleanwebm:' + id_, action + 's')
                r.hincrby('cleanwebm:' + id_, ip_action + 's', -1)
                r.hset('ip:' + ip + ":" + id_, 'action', action)
            result = r.hmget('cleanwebm:' + id_, ('likes', 'dislikes'))
            return {'md5': md5, 'id': id_, 'likes': result[0], 'dislikes': result[1],
                    'action': action}
    return