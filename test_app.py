import pytest
import os
from unittest.mock import MagicMock
from main import app, r

API_KEY = os.getenv("API_KEY")
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_redis(mocker):
    mock_redis_client = mocker.patch('main.r')
    return mock_redis_client

@pytest.fixture
def api_headers():
    return {'API_KEY': API_KEY}

def test_push_to_queue(client, mock_redis, api_headers):
    mock_redis.rpush.return_value = None

    response = client.post('/api/queue/push', json={'message': 'Test message'}, headers=api_headers)

    assert response.status_code == 200
    assert response.json == {'status': 'ok'}
    mock_redis.rpush.assert_called_once_with('message_queue', 'Test message')

def test_pop_from_queue(client, mock_redis, api_headers):
    mock_redis.lpop.return_value = 'Test message'

    response = client.post('/api/queue/pop', headers=api_headers)

    assert response.status_code == 200
    assert response.json == {'status': 'ok', 'message': 'Test message'}
    mock_redis.lpop.assert_called_once_with('message_queue')

def test_count_queue(client, mock_redis, api_headers):
    mock_redis.llen.return_value = 5

    response = client.get('/api/queue/count', headers=api_headers)

    assert response.status_code == 200
    assert response.json == {'status': 'ok', 'count': 5}
    mock_redis.llen.assert_called_once_with('message_queue')
