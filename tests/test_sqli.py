import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_sql_injection_search(client):
    # Test SQL injection in search
    response = client.post('/search', data={
        'query': "' OR 1=1 --"
    })
    assert b"admin@example.com" in response.data
    assert b"user1@example.com" in response.data

def test_sql_injection_login(client):
    # Test SQL injection in login
    response = client.post('/login', data={
        'username': "' OR 1=1 --",
        'password': "anything"
    })
    assert b"Welcome, admin" in response.data

def test_api_injection(client):
    # Test SQL injection in API
    response = client.get('/api/userinfo?id=1 OR 1=1')
    assert b"admin@example.com" in response.data
    assert b"user1@example.com" in response.data