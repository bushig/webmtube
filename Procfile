redis: redis-server
celery: celery -A tasks worker --loglevel=info
web: PYTHONUNBUFFERED=false gunicorn -b 0.0.0.0:8000 app:app