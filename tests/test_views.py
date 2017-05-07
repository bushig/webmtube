import pytest
from falcon import testing
from falcon.status_codes import HTTP_400
from webmtube.config import TESTING_DB_ENGINE
from webmtube.app import create_app

api = create_app(TESTING_DB_ENGINE)


@pytest.fixture(scope="session")
def client():
    # api = create_app(TESTING_DB_ENGINE)
    yield testing.TestClient(api)


class TestScreamerResourse:
    def test_md5_not_exists_no_url(self, client):
        response = client.simulate_get('/check', query_string="md5=notexists")
        assert response.status_code == 400
        assert response.json == {'md5': 'notexists', 'message': 'Неправильная ссылка в запросе'}

    def test_md5_not_exists_invalid_url(self, client):
        response = client.simulate_get('/check', query_string="md5=notexists&url=https%3A%2F%2F0chan.ru")
        assert response.status_code == 400
        assert response.json == {'md5': 'notexists', 'message': 'Неправильная ссылка в запросе'}

    def test_md5_not_exists_valid_url(self, client):
        response = client.simulate_get('/check',
                                       query_string="md5=notexists&url=https%3A%2F%2F2ch.hk%2Fb%2Fsrc%2F152501896%2F14940948899400.webm")
        assert response.status_code == 202
        assert response.json == {'md5': 'notexists', 'message': 'Добавлено в очередь на анализ'}

    def test_md5_being_analyzed_valid_url_given(self, client):
        response = client.simulate_get('/check',
                                       query_string="md5=notexists&url=https%3A%2F%2F2ch.hk%2Fb%2Fsrc%2F152501896%2F14940948899400.webm")
        assert response.status_code == 202
        assert response.json == {'md5': 'notexists', 'message': 'Уже анализируется'}

    def test_md5_being_analyzed_invalid_url_given(self, client):
        response = client.simulate_get('/check', query_string="md5=notexists&url=invalid")
        assert response.status_code == 202
        assert response.json == {'md5': 'notexists', 'message': 'Уже анализируется'}

    def test_md5_being_analyzed_none_url_given(self, client):
        response = client.simulate_get('/check', query_string="md5=notexists")
        assert response.status_code == 202
        assert response.json == {'md5': 'notexists', 'message': 'Уже анализируется'}
