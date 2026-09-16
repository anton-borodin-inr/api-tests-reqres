# api-tests-reqres

A Python learning project for API testing with `requests` and `pytest`. It covers two separate ReqRes surfaces: classic `/api/users` examples and a persistent `products` collection in `noble-harbor-api`.

**Stack:** Python 3.14 · `requests` · `pytest` · `python-dotenv`

## Project structure

| File | Purpose |
|---|---|
| `test_users.py` | Eight classic `/api/users` tests: authentication, pagination, response fields, missing resources and malformed JSON |
| `test_products.py` | One persistent product lifecycle: POST → GET → PUT → GET → DELETE → GET 404 |
| `config.py` | Loads and validates the persistent API configuration |
| `conftest.py` | Provides the `api_session` fixture with shared headers and query parameters |
| `.env.example` | Configuration template without API key values |

The goal is to practise checking status codes, response structure, field types and values, and to distinguish observed behaviour from the expected contract.

## Quick start

```bash
git clone https://github.com/anton-borodin-inr/api-tests-reqres.git
cd api-tests-reqres

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

Fill in `.env` with your credentials and configuration for both API surfaces. The persistent lifecycle requires access to an existing `products` collection. The learning project uses `noble-harbor-api`, project ID `45121`; use a project and collection you can access.

### Configuration

| Variable | Meaning |
|---|---|
| `REQRES_API_KEY` | Key for the classic users tests |
| `REQRES_BASE_URL` | Base URL for the classic users tests |
| `NOBLE_API_KEY` | Key for the persistent collection, sent as `x-api-key` |
| `NOBLE_BASE_URL` | Base URL for the persistent collection |
| `NOBLE_REQRES_ENV` | Environment sent as `x-reqres-env` |
| `NOBLE_PROJECT_ID` | Project ID sent as the `project_id` query parameter |

Keep the `REQRES_*` and `NOBLE_*` settings separate. `.env` is ignored by Git; do not commit credentials.

Configuration is validated at import time. Because the root `conftest.py` imports `config.py`, the `NOBLE_*` settings are required even when collecting or running only the classic users tests. The users module also validates its own `REQRES_*` settings when imported.

### Run tests

Collect tests without sending HTTP requests:

```bash
pytest --collect-only -q
```

Run only the persistent lifecycle:

```bash
pytest -q test_products.py::test_product_lifecycle
```

Run the classic tests or the complete suite:

```bash
pytest -q test_users.py
pytest -v
```

The lifecycle creates, updates and deletes a real record. Classic tests also include POST requests. The complete suite is not currently expected to be all green; see the observations below.

## Persistent product lifecycle

The test creates a product with `price: 100`, reads it independently, updates the price to `200`, reads it again, deletes the record, and verifies a final `404` with `error == "record_not_found"`.

Independent GET requests check persistence: a successful mutation response or an echo of submitted values alone is not sufficient evidence. The response envelope separates record metadata (`body["data"]`) from product fields (`record["data"]`); the record ID is a string. After the update, the test checks the new price and the unchanged name, category and stock flag. Timestamp checks cover presence, not their values or progression. The DELETE response is checked for `204` without parsing JSON.

`api_session` uses `scope="function"`: each requesting test gets its own `requests.Session`. The fixture sets headers and `project_id`, yields the client, and closes it through a context manager after the test, including an ordinary assertion failure. Each request supplies its own timeout.

**Closing the client does not delete the product.** DELETE is still part of the test body. A failure before that step can leave a record behind; product cleanup in teardown is not implemented yet.

PATCH is excluded from this scenario. In an earlier manual experiment, its `200` response echoed an update that an independent GET did not find persisted.

## Classic users tests

| Test | Current assertions |
|---|---|
| `test_request_without_api_key_returns_401` | 401, `missing_api_key`, and presence of `message` |
| `test_api_key_accepted_in_query_param` | 200 and the requested page when the key is supplied in the query |
| `test_get_users_list_returns_requested_page` | 200 and the requested page with header authentication |
| `test_request_with_invalid_api_key_in_query_returns_403` | 403 and `invalid_api_key` |
| `test_get_single_user_returns_expected_user` | 200, a `data` envelope, integer ID and the requested ID value |
| `test_get_nonexistent_user_returns_404` | 404 with valid authentication supplied |
| `test_create_user_returns_201` | 201, echoed name/job, presence of `createdAt`/`id`, and integer ID |
| `test_post_malformed_json_returns_400` | 400 and `invalid_json` for deliberately truncated JSON |

The malformed-body test uses `data=` and an explicit `Content-Type`; other JSON submissions use `json=`.

### Validation and unresolved observations

- After the fixture was moved to `conftest.py`, the learner reported **1 passed** for the product lifecycle. Collection was separately verified: **9 tests collected**, without HTTP requests.
- The last learner-reported full run, before the fixture/configuration refactor, was **7 passed, 2 failed**. The complete suite has not been rerun after that refactor.
- The missing-key test expected `401` but received `200`. The cause remains unverified; caching is only a hypothesis.
- The classic POST test expected an integer ID but received a string (for example, `'395'`). A difference from the GET representation alone does not establish a server defect: the endpoint contracts need to be checked separately.

These assertions remain unchanged pending investigation. Neither failure has been marked `xfail`. Earlier manual notes also recorded differences in response envelopes, naming, error fields and documentation links. They are investigation leads, not verified current defects or evidence that a client necessarily crashes.

## Next steps

- parameterize the authentication cases and compare the results with a loop-based check
- investigate the two classic-test failures against the expected contracts
- practise markers and the distinction between `skip` and `xfail`
- add JSON Schema validation
- address product cleanup after a failed lifecycle
- build a separate suite for an API with pagination and filtering
