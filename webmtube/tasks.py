import celery
from celery import Celery

from webmtube.caching import set_cache, del_dirty_cache, set_dirty_cache
from webmtube.config import BROKER
from webmtube.models import WEBM, Session, DirtyWEBM
from webmtube.scream_detector import get_scream_chance
from webmtube.utils import get_file_md5, download_file
from webmtube.webm_striper import strip_webm, hash_stripped_webm

# Celery instance
app = Celery('tasks', broker=BROKER)


# celery_log = logging.getLogger('celery')


class BaseTaskHandler(celery.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('Произошла ошибка во время выполнения Таска, удаляем кэш')
        del_dirty_cache(args[0])


@app.task(base=BaseTaskHandler, ignore_result=True)
def analyse_video(md5, url):# TODO: Rename to smth
    try:
        # celery_log.info('Downloading new video with url of %s' % (url,))
        file = download_file(url)
        if get_file_md5(file) != md5:
            raise Exception('md5 not the same.')
        screamer_chance = get_scream_chance(file.name)
        print(file.name)
        strip_filename = strip_webm(file.name)
        strip_md5 = hash_stripped_webm(strip_filename)
        # celery_log.info('Calculated screamer chance is %s. Adding WEBM to DB' % (screamer_chance,))
        #print(screamer_chance)
        session = Session()
        print(strip_md5, screamer_chance)
        webm = session.query(WEBM).get(strip_md5)
        # Was not in DB
        if webm is None:
            webm = WEBM(id_=strip_md5, screamer_chance=screamer_chance)
            session.add(webm)
        dirty_webm = DirtyWEBM(md5=md5, webm_id=strip_md5)
        session.add(dirty_webm)
        session.commit()
        del_dirty_cache(
            md5)  # TODO: Delete Delayed message and set new in one transaction to prevent possible race condition
        set_dirty_cache(md5, strip_md5)
        # celery_log.info('Releasing WEBM from Celery')
        set_cache(webm.to_dict())
        return webm.to_dict()
    except Exception as e:
        print('Error encountered: {}'.format(e))


if __name__ == "__main__":
    app.start()
