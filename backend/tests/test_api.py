import requests
import os

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def test_health():
    r = requests.get(f"{BASE_URL}/health/")
    assert r.status_code == 200
    assert "status" in r.json()


def test_health_detailed():
    r = requests.get(f"{BASE_URL}/health/detailed")
    assert r.status_code == 200
    assert "services" in r.json()


def test_start_session():
    r = requests.post(f"{BASE_URL}/query/start-session", json={"user_id": "test_user"})
    assert r.status_code == 200
    data = r.json()
    assert "session_id" in data
    return data["session_id"]


def test_general_query():
    session_id = test_start_session()
    r = requests.post(f"{BASE_URL}/query/", json={"query": "What is yield farming?", "session_id": session_id})
    assert r.status_code == 200
    data = r.json()
    assert "intent" in data
    assert data["session_id"] == session_id


def test_action_request():
    session_id = test_start_session()
    r = requests.post(f"{BASE_URL}/query/", json={"query": "I want to swap 100 USDC for ETH", "session_id": session_id})
    assert r.status_code == 200
    data = r.json()
    assert "intent" in data
    assert data["session_id"] == session_id

if __name__ == "__main__":
    test_health()
    test_health_detailed()
    test_general_query()
    test_action_request()
    print("All API tests passed!")
