from webmtube.scream_detector import get_scream_chance


# ffmpeg -hide_banner -nostats -i webm_files/1.mp4 -filter_complex ebur128=meter=18 -f null -
class TestScreamDetector:
    def test_mp4(self):
        filename = 'webm_files/1.mp4'
        assert get_scream_chance(filename) == 0

    def test_webm(self):
        filename = 'webm_files/1.webm'
        assert get_scream_chance(filename) == 0

    def test_webm_screamer(self):
        filename = 'webm_files/scr1.webm'
        assert get_scream_chance(filename) == 1
