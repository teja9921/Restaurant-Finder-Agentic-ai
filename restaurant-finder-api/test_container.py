import requests

response = requests.post(
    "http://localhost:8080/invocations",
    json={
        "prompt": "Find vegan restaurants in Mumbai",
        "session_id": "test-docker",
        "customer_name": "Docker Tester"
    }
)

print(response.json())