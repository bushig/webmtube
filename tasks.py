from celery import Celery
import redis
import logging
from config import BROKER
from models import WEBM, Session
from utils import get_file_md5, download_file
from scream_detector import get_scream_chance

# Celery instance
app = Celery('tasks', broker=BROKER)

r = redis.StrictRedis(host='localhost', port=6379, db=1)
celery_log = logging.getLogger('celery')


@app.task
def analyse_video(md5, url):  # TODO: Rename to smth
    celery_log.info('Downloading new video with url of %s' % (url,))
    try:
        file = download_file(url)
        if get_file_md5(file) != md5:
            celery_log.exception('MD5 is not the same')
            raise Exception('md5 not the same.')
        screamer_chance = get_scream_chance(file.name)
        celery_log.info('Calculated screamer chance is %s. Adding WEBM to DB' % (screamer_chance,))
        # print(screamer_chance)
        session = Session()
        webm = WEBM(md5=md5, size=0, screamer_chance=screamer_chance)
        session.add(webm)
        session.commit()
        celery_log.info('Releasing WEBM from Redis')
        r.delete(md5)
        return webm
    except Exception as e:
        celery_log.exception('Error encountered: %s' % (e,))


if __name__ == "__main__":
    app.start()
