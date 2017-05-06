from os import path

import redis

# 2CH URL
DVACH_DOMAINS = ('2ch.hk', '2ch.pm', '2ch.re', '2ch.tf', '2ch.wf', '2ch.yt', '2-ch.so')
ALLOWED_BOARDS = ('b', 'gd', "pr", 'mlp')
MAX_SIZE = 22000000  # 22MB

BASE_DIR = path.abspath('')
DB_ENGINE = 'sqlite:///db.sqlite3'

# Celery configs
BROKER = 'redis://localhost:6379/0'

# Redis caching
CACHING_REDIS = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)



WEBM_PATH = path.join(BASE_DIR, 'webm_files')

## SCREAMER DETERMENITION
# GOOD = -20.0             # If lower than this not ear damaging GREEN   %0
LOUD = -12.0  # if bigger Just loud, most likely not annoying YELLOW  %50
SCREAM = -5.0  # Very loud, if bigger 80% scream ORANGE
DEFENITLY_SCREAM = -0.5  #if bigger then 100% scream RED

LOGGING_PATH = '/tmp/logs/webmtube'
LOGGING_FALCON_FILE = 'falcon.log'
LOGGING_CELERY_FILE = 'celery.log'
LOG_LEVEL = 10
