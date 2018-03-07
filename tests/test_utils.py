from webmtube.utils import is_valid_2ch_url, get_file_md5
import os

path_to_current_file = os.path.realpath(__file__)
current_directory = os.path.split(path_to_current_file)[0]

class TestIs_valid_2ch_url:
    def test_https_2ch_hk_b_valid_webm_link(self):
        assert is_valid_2ch_url("https://2ch.hk/b/src/152120959/14936167914140.webm") is True

    def test_https_2ch_hk_pr_valid_webm_link(self):
        assert is_valid_2ch_url("https://2ch.hk/pr/src/152120959/14936167914140.webm") is True

    def test_https_2ch_pm_b_valid_webm_link(self):
        assert is_valid_2ch_url("https://2ch.pm/pr/src/152120959/14936167914140.webm") is True

    def test_https_2ch_ru_b_invalid_domain(self):
        assert is_valid_2ch_url("https://2ch.ru/pr/src/152120959/14936167914140.webm") is False

    def test_https_2ch_hk_b_invalid_extension(self):
        assert is_valid_2ch_url("https://2ch.hk/b/src/15212092159/149361679141540.jpeg") is False

    def test_https_2ch_hk_ts_invalid_board(self):
        assert is_valid_2ch_url("https://2ch.hk/ts/src/152120959/14936167914140.webm") is False

    def test_https_2ch_hk_b_valid_mp4_link(self):
        assert is_valid_2ch_url("https://2ch.hk/b/src/152120959/14936167914140.mp4") is True


class TestGet_file_md5:
    def test_big(self):
        path_to_file = os.path.join(current_directory, 'webm_files/big_0.webm')
        with open(path_to_file, 'rb') as f:
            md5 = get_file_md5(f)
            assert md5 == "bdb096a73a951fc26faa1130ad6607c0"

    def test_small(self):
        path_to_file = os.path.join(current_directory, 'webm_files/scr1.webm')
        with open(path_to_file, 'rb') as f:
            md5 = get_file_md5(f)
            assert md5 == "d77423f4867e8e1bef94e57f849c50f7"

    def test_mp4(self):
        path_to_file = os.path.join(current_directory, 'webm_files/1.mp4')
        with open(path_to_file, 'rb') as f:
            md5 = get_file_md5(f)
            assert md5 == "bf0a14f73482ac994307ac885c568d15"
