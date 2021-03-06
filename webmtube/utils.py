import hashlib
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse
from urllib.request import urlopen, URLError

from webmtube import Session
from webmtube.caching import pop_webm_from_redis_list, save_webm_to_db
from webmtube.config import DVACH_DOMAINS, ALLOWED_BOARDS, MAX_SIZE


def is_valid_2ch_url(url):
    url_info = urlparse(url)
    if url_info.netloc in DVACH_DOMAINS and url_info.scheme in ('http', 'https'):
        path_info = url_info.path.split('/')[1:]
        if path_info[0] in ALLOWED_BOARDS and path_info[1] == 'src' and (
                        path_info[3][-5:].lower() == '.webm' or path_info[3][-4:].lower() == '.mp4'):
            return True
    return False


def before_shutdown_handler():
    # TODO: save all data from redis to db and flush it
    # Use bulk_update_mappings
    print('Shutting down')
    counter = 0
    session = Session()
    while True:
        md5 = pop_webm_from_redis_list()  # TODO: use sscans iteration of clean_md5
        if md5 is None:
            break
        save_webm_to_db(md5, session)
        counter += 1
        print("Saved webm #{} to DB: {}".format(counter, md5))
    print("Saved ", counter, "in total")


def get_file_md5(file):
    h = hashlib.md5()
    file.seek(0)
    for chunk in iter(lambda: file.read(4096), b""):
        h.update(chunk)
    return h.hexdigest()


def download_file(url):
    """Download webm and pass file exemplar"""
    try:
        u = urlopen(url)
    except URLError as e:
        print("Error: {} while opening webm url: {}".format(e, url))
        raise URLError('Link open error')

    file_size = int(u.getheader("Content-Length"))
    if file_size > MAX_SIZE:
        raise Exception("WEBM size is too big. Allowed: {0}, File size: {1}".format(MAX_SIZE, file_size))
    f = NamedTemporaryFile('w+b', suffix=".webm")
    print("Downloading: WEBM: {} Bytes: {}".format(url, file_size))
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        # status = "{10d}  [%3.2f%%]".format(file_size_dl, file_size_dl * 100. / file_size)
        # status = status + chr(8)*(len(status)+1)
        # print (status)
    print("Downloaded WEBM: {}".format(url))
    return f


    # download_file("https://2ch.hk/b/src/138643380/14774809289143.webm")
    # print(is_valid_2ch_url("https://2ch.hk/b/src/138764699/14776101349660.webm"))
