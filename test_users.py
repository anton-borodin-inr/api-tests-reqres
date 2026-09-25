import pytest
import requests
from config import reqres_base_url, reqres_api_key, TIMEOUT, REQRES_AUTH_HEADERS


def test_request_without_reqres_api_key_returns_401():
    response = requests.get(f"{reqres_base_url}/api/users", params={"page": 2}, timeout=TIMEOUT)
    assert response.status_code == 401, f"Expected 401 for no api key, got {response.status_code}"
    body = response.json()
    error_code = body.get("error")
    assert error_code == "missing_api_key", f"Expected error 'missing_api_key', got {error_code}"
    assert "message" in body, f"Response has no 'message' field: {body}"


def test_reqres_api_key_accepted_in_query_param():
    response = requests.get(f"{reqres_base_url}/api/users", params={"page": 2, "api_key": reqres_api_key}, timeout=TIMEOUT)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    page_number = response.json().get("page")
    assert page_number == 2, f"Expected page 2, got {page_number}"


def test_get_users_list_returns_requested_page():
    response = requests.get(f"{reqres_base_url}/api/users", params={"page": 2}, headers=REQRES_AUTH_HEADERS, timeout=TIMEOUT)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    page_number = response.json().get("page")
    assert page_number == 2, f"Expected page 2, got {page_number}"


def test_request_with_invalid_reqres_api_key_in_query_returns_403():
    response = requests.get(f"{reqres_base_url}/api/users", params={"page": 2, "api_key": "definitely_invalid_reqres_api_key"},
                            timeout=TIMEOUT)
    assert response.status_code == 403, f"Expected 403 for invalid api key, got {response.status_code}"
    error_code = response.json().get("error")
    assert error_code == "invalid_api_key", f"Expected error 'invalid_api_key', got {error_code}"


def test_get_single_user_returns_expected_user():
    response = requests.get(f"{reqres_base_url}/api/users/2", headers=REQRES_AUTH_HEADERS, timeout=TIMEOUT)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    body = response.json()
    assert "data" in body, f"Response has no 'data' field: {body}"
    user_id = body["data"]["id"]
    assert isinstance(user_id, int), f"Expected 'id' to be int, got {type(user_id).__name__}"
    assert user_id == 2, f"Expected user id 2, got {user_id}"


def test_get_nonexistent_user_returns_404():
    response = requests.get(f"{reqres_base_url}/api/users/23", headers=REQRES_AUTH_HEADERS, timeout=TIMEOUT)
    assert response.status_code == 404, f"Expected 404 for nonexistent user, got {response.status_code}"


@pytest.mark.xfail(reason="POST returns a string id; test expects an integer", strict=True)
def test_create_user_returns_201():
    payload = {"name": "anton", "job": "qa"}
    response = requests.post(f"{reqres_base_url}/api/users", headers=REQRES_AUTH_HEADERS, json=payload, timeout=TIMEOUT)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    body = response.json()
    assert body["name"] == payload["name"], f"Expected name {payload['name']}, got {body['name']}"
    assert body["job"] == payload["job"], f"Expected job {payload['job']}, got {body['job']}"
    assert "createdAt" in body
    assert "id" in body
    assert isinstance(body["id"], int), f"Expected 'id' to be int, got {type(body['id']).__name__}"


def test_post_malformed_json_returns_400():
    headers = {**REQRES_AUTH_HEADERS, "Content-Type": "application/json"}
    response = requests.post(f"{reqres_base_url}/api/users", headers=headers, data='{"name": "anton"', timeout=TIMEOUT)
    assert response.status_code == 400, f"Expected 400 for malformed json, got {response.status_code}"
    error_code = response.json().get("error")
    assert error_code == "invalid_json", f"Expected invalid json, got {error_code}"
