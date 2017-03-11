from celery import Celery
from urllib.error import URLError
import logging
from config import BROKER
from models import WEBM, Session
from utils import get_file_md5, download_file
from scream_detector import get_scream_chance
from caching import set_cache, del_cache

# Celery instance
app = Celery('tasks', broker=BROKER)

celery_log = logging.getLogger('celery')


@app.task(autoretry_for=(URLError,), ignore_result=True)
def analyse_video(md5, url):# TODO: Rename to smth
    try:
        celery_log.info('Downloading new video with url of %s' % (url,))
        file = download_file(url)
        if get_file_md5(file) != md5:
            raise Exception('md5 not the same.')
        screamer_chance = get_scream_chance(file.name)
        celery_log.info('Calculated screamer chance is %s. Adding WEBM to DB' % (screamer_chance,))
        #print(screamer_chance)
        session = Session()
        webm = WEBM(md5=md5, screamer_chance=screamer_chance)
        session.add(webm)
        session.commit()
        del_cache(md5)  # TODO: Delete Delayed message and set new in one transaction to prevent possible race condition
        celery_log.info('Releasing WEBM from Celery')
        set_cache(webm.to_dict())
        return webm
    except Exception as e:
        celery_log.exception('Error encountered: %s' % (e,))


if __name__ == "__main__":
    app.start()
