from webmtube.utils import is_valid_2ch_url


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
