from webmtube.caching import set_cache, del_all_dirty_cache, get_cache, incr_views, like_webm, save_webm_to_db, \
    check_ip_viewed, set_dirty_cache, set_cache_delayed, get_dirty_cache, get_clean_cache
from webmtube.config import CACHING_REDIS as r

from sqlalchemy.engine import create_engine
from sqlalchemy_utils.functions import drop_database

from webmtube.models import Base, DirtyWEBM, WEBM


def setup_module():
    r.flushall()
    # Setup DB
    global connection, engine
    # Connect to the database and create the schema within a transaction
    engine = create_engine('sqlite:///test_db.sqlite3')  # TODO: move to config
    connection = engine.connect()
    Base.metadata.create_all(connection)

    # If you want to insert fixtures to the DB, do it here


def teardown_module():
    r.flushall()
    connection.close()
    engine.dispose()
    drop_database(engine.url)


data = {"id": "scream05", "views": 50, "likes": 10,
        "dislikes": 5, "time_created": "2017-05-04T20:35:45",
        "screamer_chance": 0.5}


class TestSet_cache():
    def test_good_data(self):
        assert set_cache(data) is True

    def test_duplicate_data(self):
        assert set_cache(data) is False

    def test_none_screamer_chance(self):
        data_n = data.copy()
        data_n["id"] = "screamnone"
        data_n["screamer_chance"] = None
        assert set_cache(data_n) is True

    def test_1_screamer_chance(self):
        data_n = data.copy()
        data_n["id"] = "scream1"
        data_n["screamer_chance"] = 1
        assert set_cache(data_n) is True

    def test_0_screamer_chance(self):
        data_n = data.copy()
        data_n["id"] = "scream0"
        data_n["screamer_chance"] = 0
        assert set_cache(data_n) is True


class TestDirty_cache():
    def test_set_dirty_delayed(self):
        set_cache_delayed("md5delay")
        assert get_dirty_cache("md5delay") == "delayed"

    def test_set_with_nonexisting_clean(self):
        set_dirty_cache('md5noclean', 'justrandom')
        assert get_dirty_cache('md5noclean') == 'justrandom'

    def test_set_good(self):
        set_dirty_cache('md5screamnone', 'screamnone')
        set_dirty_cache('md5scream1', 'scream1')
        set_dirty_cache('md5scream05', 'scream05')
        set_dirty_cache('md5scream0', 'scream0')


class TestGet_cache():
    def test_not_existing_cache(self):
        assert get_cache("notexists") is None

    def test_data_in_DB(self):
        pass

    def test_delayed_cache(self):
        assert get_cache("md5delay") is "delayed"

    def test_existing_cache_with_none_screamer_chance(self):
        result = get_cache("md5screamnone")
        assert result["screamer_chance"] is None

    def test_existing_cache_with_1_screamer_chance(self):
        result = get_cache("md5scream1")
        assert result["screamer_chance"] == "1"

    def test_existing_cache_with_0_5_screamer_chance(self):
        result = get_cache("md5scream05")
        assert result["screamer_chance"] == "0.5"

    def test_existing_cache_with_0_screamer_chance(self):
        result = get_cache("md5scream0")
        assert result["screamer_chance"] == "0"
