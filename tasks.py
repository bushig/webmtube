from celery import Celery
import redis

from config import BROKER
from models import WEBM, Session
from utils import get_file_md5, download_file
from scream_detector import get_scream_chance

# Celery instance
app = Celery('tasks', broker=BROKER)

r = redis.StrictRedis(host='localhost', port=6379, db=1)

@app.task
def analyse_video(md5, url):  # TODO: Rename to smth
    file = download_file(url)
    if get_file_md5(file) != md5:
        raise Exception('md5 not the same.')
    screamer_chance = get_scream_chance(file.name)
    print(screamer_chance)
    session = Session()
    webm = WEBM(md5=md5, size=0, screamer_chance=screamer_chance)
    session.add(webm)
    session.commit()
    r.delete(md5)
    return webm


if __name__ == "__main__":
    app.start()
