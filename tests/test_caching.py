import pytest

from webmtube.caching import set_cache, del_all_dirty_cache, get_cache, incr_views, like_webm, save_webm_to_db, \
    check_ip_viewed, set_dirty_cache, set_cache_delayed, get_dirty_cache, get_clean_cache
from webmtube.config import CACHING_REDIS as r

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import drop_database

from webmtube.models import Base, DirtyWEBM, WEBM
from webmtube.app import create_app


def setup_module():
    r.flushall()
    # Setup DB
    global session, engine, api
    # Connect to the database and create the schema within a transaction
    engine = create_engine('sqlite:///test_db.sqlite3')  # TODO: move to config
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    api = create_app('sqlite:///test_db.sqlite3')

    # If you want to insert fixtures to the DB, do it here
    clean = WEBM(id_="dbcleannone")
    clean2 = WEBM(id_="dbclean1", screamer_chance=1)
    clean3 = WEBM(id_="dbclean0_5", screamer_chance=0.5)

    dirty = DirtyWEBM(md5="dbdirtynone", webm_id="dbcleannone")
    dirty_dup = DirtyWEBM(md5="dbdirtynone_dup", webm_id="dbcleannone")
    dirty2 = DirtyWEBM(md5="dbdirty0_5", webm_id="dbclean0_5")
    dirty3 = DirtyWEBM(md5="dbdirty1", webm_id="dbclean1")
    session.add_all([clean, clean2, clean3, dirty, dirty_dup, dirty2, dirty3])
    session.commit()



def teardown_module():
    global api
    del api  # Hope it works
    r.flushall()
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

    def test_set_duplicate(self):
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

    def test_data_from_DB_none(self):
        data = get_cache("dbdirtynone")
        assert data["id"] == "dbcleannone"
        assert data["screamer_chance"] is None

        dup_data = get_cache("dbdirtynone_dup")
        assert dup_data["id"] == "dbcleannone"
        assert dup_data["screamer_chance"] is None

    def test_data_from_DB_1(self):
        data = get_cache("dbdirty1")
        assert data["id"] == "dbclean1"
        assert data["screamer_chance"] == 1.0
        # Retry the same
        data = get_cache("dbdirty1")
        assert data["id"] == "dbclean1"
        assert data["screamer_chance"] == "1.0"  # Should fix later


    def test_delayed_cache(self):
        assert get_cache("md5delay") == "delayed"

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


class TestIncr_views():
    ip = "15.25.61.5"

    def test_md5_in_cache(self):
        assert check_ip_viewed("dbdirtynone", self.ip) is False
        assert incr_views(self.ip, "dbdirtynone") is True
        assert get_cache("dbdirtynone")["views"] == "1"

        assert isinstance(check_ip_viewed("dbdirtynone", self.ip), int)

        assert incr_views(self.ip, "dbdirtynone") is True
        assert get_cache("dbdirtynone")["views"] == "2"

    def test_md5_same_clear(self):
        # Different md5, and shouldn't be incremented
        assert isinstance(check_ip_viewed("dbdirtynone_dup", self.ip), int)
        assert incr_views(self.ip, "dbdirtynone_dup") is True
        assert get_cache("dbdirtynone")["views"] == "3"

        # diff IP
        assert incr_views("12.21.52.1", "dbdirtynone_dup") is True
        assert get_cache("dbdirtynone")["views"] == "4"

    def test_md5_in_DB(self):
        assert incr_views(self.ip, "dbdirty0_5") is False
        assert check_ip_viewed("dbdirty0_5", self.ip) is False

    def test_md5_not_exists(self):
        assert incr_views(self.ip, "qweaweqq") is False
        assert check_ip_viewed("qweaweqq", self.ip) is False


class TestLike_webm():
    ip = "15.25.61.5"

    def test_in_cache(self):
        # add like
        data = like_webm("dbdirtynone", self.ip, "like")
        assert data["likes"] == "1"
        assert data["dislikes"] == "0"
        assert data["action"] == "like"

        # remove like
        data = like_webm("dbdirtynone", self.ip, "like")
        assert data["likes"] == "0"
        assert data["dislikes"] == "0"
        assert data["action"] == None

        # add dislike
        data = like_webm("dbdirtynone", self.ip, "dislike")
        assert data["likes"] == "0"
        assert data["dislikes"] == "1"
        assert data["action"] == "dislike"

        # remove dislike
        data = like_webm("dbdirtynone", self.ip, "dislike")
        assert data["likes"] == "0"
        assert data["dislikes"] == "0"
        assert data["action"] == None

        # add like to other md5
        data = like_webm("dbdirtynone_dup", self.ip, "like")
        assert data["likes"] == "1"
        assert data["dislikes"] == "0"
        assert data["action"] == "like"

        # set like to dislike
        data = like_webm("dbdirtynone_dup", self.ip, "dislike")
        assert data["likes"] == "0"
        assert data["dislikes"] == "1"
        assert data["action"] == "dislike"
