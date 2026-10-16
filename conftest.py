import json
from pathlib import Path
import pytest
import requests
from config import project_id, NOBLE_AUTH_HEADERS


@pytest.fixture(scope="function")
def api_session():
    with requests.Session() as s:
        s.params = {"project_id": project_id}
        s.headers.update(NOBLE_AUTH_HEADERS)
        yield s


@pytest.fixture(scope="session")
def product_record_schema():
    schema_path = Path(__file__).parent / "schemas" / "product_record.schema.json"
    text = schema_path.read_text()
    schema = json.loads(text)
    return schema
