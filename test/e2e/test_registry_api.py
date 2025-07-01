import requests
import os

REGISTRY_URL = os.environ.get("AGENT_REGISTRY_URL", "http://localhost:5002")

def test_get_agents():
    url = f"{REGISTRY_URL}/agents"
    resp = requests.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    print("/agents GET OK", data)

def test_post_agent():
    url = f"{REGISTRY_URL}/agents"
    agent = {
        "artifactID": "test.example.com/test_agent",
        "name": "TestAgent",
        "description": "for test",
        "capabilities": ["test_task"],
        "endpoint": "http://test_agent:5000",
        "status": "active",
        "tasks": [
            {"type": "test_task", "requires_consent": False}
        ]
    }
    resp = requests.post(url, json=agent)
    assert resp.status_code in (200, 201)
    print("/agents POST OK", resp.json())

if __name__ == "__main__":
    test_post_agent()
    test_get_agents()
