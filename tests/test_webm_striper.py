import os

from webmtube.webm_striper import hash_stripped_webm, strip_webm

path_to_current_file = os.path.realpath(__file__)
current_directory = os.path.split(path_to_current_file)[0]


class TestWebm_striper:
    orig_md5 = "f433f19f75139dda418e9029b00dfb9c"

    def test_duplicate_1(self):
        path_to_file = os.path.join(current_directory, 'webm_files/duplicates/1.webm')
        filename = strip_webm(path_to_file)
        assert os.path.isfile(filename)
        md5 = hash_stripped_webm(filename)
        assert os.path.isfile(filename) is False
        assert md5 == self.orig_md5

    def test_duplicate_doll(self):
        path_to_file = os.path.join(current_directory, 'webm_files/duplicates/1_doll.webm')
        filename = strip_webm(path_to_file)
        assert os.path.isfile(filename)
        md5 = hash_stripped_webm(filename)
        assert os.path.isfile(filename) is False
        assert md5 == self.orig_md5

    def test_duplicate_doll_EXIF(self):
        path_to_file = os.path.join(current_directory, 'webm_files/duplicates/1_dollEXIF.webm')
        filename = strip_webm(path_to_file)
        assert os.path.isfile(filename)
        md5 = hash_stripped_webm(filename)
        assert os.path.isfile(filename) is False
        assert md5 == self.orig_md5

    def test_big(self):
        path_to_file = os.path.join(current_directory, 'webm_files/big_0.webm')
        filename = strip_webm(path_to_file)
        assert os.path.isfile(filename)
        md5 = hash_stripped_webm(filename)
        assert os.path.isfile(filename) is False
        assert md5 == "c48cb49d94ebcea4afd685f4fcbf9c0a"
