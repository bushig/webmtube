from os import path

# 2CH URL
DVACH_DOMAINS = ('2ch.hk',)
ALLOWED_BOARDS = ('b', 'gd', "pr", 'mlp')
MAX_SIZE = 22000000  # 22MB

BASE_DIR = path.abspath('')
DB_ENGINE = 'sqlite:///db.sqlite3'

# Celery configs
BROKER = 'redis://localhost:6379/0'

# Redis caching
CACHING_HOST = 'redis://localhost:6379/1'
LIKES_HOST = 'redis://localhost:6379/2'

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
