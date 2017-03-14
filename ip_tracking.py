import redis
from models import Session, WEBM

r = redis.StrictRedis(host='localhost', port=6379, db=2, decode_responses=True)
