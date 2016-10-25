from models import Session, WEBM


# TODO: create celery worker that will: Download webm, analyze it(check md5 and sound) and delete
# ffmpeg -i "input.webm" -vn -acodec copy "output.oga" to extract audio, then use LIBROSA or PyDUB

def detect_scream(md5, url):
    session = Session()
    webm = WEBM(md5=md5, size=0)
    session.add(webm)
    session.commit()
    return webm
