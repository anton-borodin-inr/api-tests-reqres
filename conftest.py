import pytest
import requests
from config import project_id, NOBLE_AUTH_HEADERS


@pytest.fixture(scope="function")
def api_session():
    with requests.Session() as s:
        s.params = {"project_id": project_id}
        s.headers.update(NOBLE_AUTH_HEADERS)
        yield s
