import os
from dotenv import load_dotenv

load_dotenv()

TIMEOUT = 10

# Configuration for "Noble" project
def read_and_check_configuration_noble():
    api_key = os.getenv("NOBLE_API_KEY")
    base_url = os.getenv("NOBLE_BASE_URL")
    reqres_env = os.getenv("NOBLE_REQRES_ENV")
    project_id = os.getenv("NOBLE_PROJECT_ID")
    if not api_key:
        raise ValueError("NOBLE_API_KEY is required. Add it to your .env file.")
    if not base_url:
        raise ValueError("NOBLE_BASE_URL is required. Add it to your .env file.")
    if not reqres_env:
        raise ValueError("NOBLE_REQRES_ENV required. Add it to your .env file.")
    if not project_id:
        raise ValueError("NOBLE_PROJECT_ID required. Add it to your .env file.")
    return api_key, base_url, reqres_env, project_id


noble_api_key, noble_base_url, reqres_env, project_id = read_and_check_configuration_noble()

NOBLE_AUTH_HEADERS = {"x-api-key": noble_api_key, "x-reqres-env": reqres_env}


# Configuration for "REQRES" project
def read_and_check_configuration_reqres():
    api_key = os.getenv("REQRES_API_KEY")
    base_url = os.getenv("REQRES_BASE_URL")
    if not api_key:
        raise ValueError("REQRES_API_KEY is required. Add it to your .env file.")
    if not base_url:
        raise ValueError("REQRES_BASE_URL is required. Add it to your .env file.")
    return api_key, base_url


reqres_api_key, reqres_base_url = read_and_check_configuration_reqres()

REQRES_AUTH_HEADERS = {"x-api-key": reqres_api_key}