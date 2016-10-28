from os import path
from tempfile import TemporaryFile
import subprocess
import re

from models import Session, WEBM
from config import WEBM_PATH, LOUD, SCREAM, DEFENITLY_SCREAM
from utils import download_file, get_file_md5


# TODO: create celery worker that will: Download webm, analyze it(check md5 and sound) and delete
# ffmpeg -i '14774809289143.webm' -ac 1 -vn 'test.wav' to extract audio, then use LIBROSA or PyDUB

def determine_scream_chance(parsed):
    print(parsed)
    if any(v >= DEFENITLY_SCREAM for v in parsed.values()):
        print(parsed.values())
        return 1.0
    elif any(v >= SCREAM for v in parsed.values()):
        return 0.8
    elif any(v >= LOUD for v in parsed.values()):
        return 0.5
    else:
        return 0.0


def parse_ffmpeg_output(file):
    """
    :param file: Data from stderr of ffmpeg
    :type file: TemporaryFile object
    """
    parsed_data = []
    line_reg = re.compile(r"\[Parsed_ebur128_\d @ [0-9a-z]{2,16}\]\s+"
                          "t:\s*([\d.]+)\s+"  # Current time in seconds
                          "M:\s*([-\d.]+)\s+"  # Momentary (0.4 sec)
                          "S:\s*([-\d.]+)\s+"  # Short-Term (3 sec)
                          "I:\s*([-\d.]+) LUFS\s+"  # Integrated
                          "LRA:\s*([-\d.]+) LU\s+"  # Range amplitude
                          )
    M = -120.0
    S = -120.0
    for line in file:
        match = re.match(line_reg, line)
        if match:
            M = max(M, float(match.group(2)))
            S = max(S, float(match.group(3)))
    return determine_scream_chance({"M": M, "S": S})


def get_scream_chance(filename):
    """
    :param filename: Video filename with extension (e.g. file.webm)
    :type filename: str
    """

    file_path = filename

    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", file_path, "-filter_complex", "ebur128=meter=18",
           "-f", "null", "-"]

    with TemporaryFile(mode='w+', encoding='utf-8') as output:
        process = subprocess.run(cmd, stderr=output)
        if process.returncode != 0:
            scream_chance = None  # Means there is no sound (actually not always)
        else:
            output.seek(0)
            scream_chance = parse_ffmpeg_output(output)
    return scream_chance


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
    return webm


    #analyse_video('a67cdcc6f30de9cdfc906bb9776fcf17', 'https://2ch.hk/b/src/138760856/14776051634640.webm')
