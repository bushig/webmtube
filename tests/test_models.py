import pytest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session
from sqlalchemy_utils.functions import drop_database
from sqlalchemy.exc import IntegrityError

from webmtube.models import Base, WEBM, DirtyWEBM


def setup_module():
    global connection, engine
    # Connect to the database and create the schema within a transaction
    engine = create_engine('sqlite:///test_db.sqlite3')  # TODO: move test_db to config + make it postgres
    connection = engine.connect()
    Base.metadata.create_all(connection)
    # If you want to insert fixtures to the DB, do it here


def teardown_module():
    # Roll back the top level transaction and disconnect from the database
    connection.close()
    engine.dispose()
    drop_database(engine.url)


class TestWEBM:
    def test_create_none_screamer_chance_default(self):
        session = Session(connection)
        webm = WEBM(id_="q")  # TODO: add 32 length constrait
        session.add(webm)
        session.commit()

    def test_get_none_screamer_chance_default(self):
        session = Session(connection)
        webm = session.query(WEBM).get('q')
        assert webm.id == 'q'
        assert webm.screamer_chance is None

    def test_delete_none_sceamer_chance_default(self):
        session = Session(connection)
        webm = session.query(WEBM).get('q')
        assert webm
        session.delete(webm)
        session.commit()
        webm = session.query(WEBM).get('q')
        assert webm is None

    def test_create_zero_screamer_chance(self):
        session = Session(connection)
        webm = WEBM(id_="q", screamer_chance=0)
        session.add(webm)
        session.commit()

    def test_get_zero_screamer_chance(self):
        session = Session(connection)
        webm = session.query(WEBM).get('q')
        assert webm.id == 'q'
        assert webm.screamer_chance == 0


class TestDirtyWEBM:
    def test_create_without_foreign_key(self):
        """Foreign key is required"""
        session = Session(connection)
        with pytest.raises(IntegrityError):
            dirty_webm = DirtyWEBM(md5="a1")  # TODO: add 32 length constrait
            session.add(dirty_webm)
            session.commit()

    # Dunno how to add FK constrait
    # def test_create_not_existing_foreign_key(self):
    #     session = Session(connection)
    #     #with pytest.raises(IntegrityError):
    #     dirty_webm = DirtyWEBM(md5="a2", webm_id="azer")
    #     session.add(dirty_webm)
    #     session.commit()

    def test_create_normal_foreign_key(self):
        session = Session(connection)
        dirty_webm = DirtyWEBM(md5="a4", webm_id="q")
        session.add(dirty_webm)
        session.commit()

    def test_get_normal_webm_reference(self):
        session = Session(connection)
        dirty_webm = session.query(DirtyWEBM).get("a4")
        assert dirty_webm.webm.id == "q"


class TestWEBMAndDirtyWEBM:
    def test_cascade_delete(self):
        session = Session(connection)
        webm = session.query(WEBM).get("q")
        session.delete(webm)
        session.commit()
        assert session.query(DirtyWEBM).get('a4') is None
