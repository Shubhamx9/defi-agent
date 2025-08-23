import requests
import os

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

client = requests.Session()
client.user_id = None
client.session_id = None


def test_health():
    r = client.get(f"{BASE_URL}/health/")
    assert r.status_code == 200
    assert "status" in r.json()


def test_health_detailed():
    r = client.get(f"{BASE_URL}/health/detailed")
    assert r.status_code == 200
    assert "services" in r.json()


def test_login():
    r = client.post(f"{BASE_URL}/auth/login")
    assert r.status_code == 200
    data = r.json()
    assert "message" in data
    client.user_id = data["user_id"]
    client.session_id = data["session_id"]


def test_general_query():
    r = client.post(
        f"{BASE_URL}/query/",
        json={
            "query": "What is yield farming?",
            "user_id": client.user_id,
            "session_id": client.session_id
        }
    )
    assert r.status_code == 200
    data = r.json()
    assert "intent" in data
    assert "session_id" in data


def test_action_request():
    r = client.post(
        f"{BASE_URL}/query/",
        json={
            "query": "I want to swap 100 USDC for ETH",
            "user_id": client.user_id,
            "session_id": client.session_id
        }
    )
    assert r.status_code == 200
    data = r.json()
    assert "intent" in data
    assert "session_id" in data


def test_logout():
    r = client.post(f"{BASE_URL}/auth/logout", cookies={"user_id": client.user_id, "session_id": client.session_id})
    assert r.status_code == 200
    data = r.json()
    assert "message" in data


if __name__ == "__main__":
    test_health()
    test_health_detailed()
    test_login()
    test_general_query()
    test_action_request()
    test_logout()
    print("All API tests passed with cookie sessions!")
