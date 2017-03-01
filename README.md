# WEBMtube
Service to detect screamers on 2ch.hk

#Requirements
* FFmpeg
* Redis
* SSL certificate

#How to start
`honcho start`

* Start redis server
`redis-server`
* Start Celery
`celery -A tasks worker --loglevel=info`
* Start app itself
`gunicorn app:app`