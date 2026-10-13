# api-tests-reqres

A Python learning project for API testing with `requests` and `pytest`. It covers two separate ReqRes surfaces: classic `/api/users` examples and a persistent `products` collection in `noble-harbor-api`.

**Stack:** Python 3.14 · `requests` · `pytest` · `python-dotenv`

## Project structure

| File | Purpose |
|---|---|
| `test_users.py` | Nine classic `/api/users` tests: authentication, pagination, response fields, missing resources, malformed JSON and an expected-failure check for the POST ID type |
| `test_products.py` | Four cases: valid-key access, two parametrized authentication rejections, and the persistent product lifecycle |
| `config.py` | Loads and validates separate Classic ReqRes and Noble settings, with a shared timeout |
| `conftest.py` | Provides the `api_session` fixture with shared headers and query parameters |
| `pytest.ini` | Test discovery settings, registered markers and default verbose output |
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

Both configuration groups are validated at import time in `config.py`. Exported names such as `reqres_base_url` / `noble_base_url` and `REQRES_AUTH_HEADERS` / `NOBLE_AUTH_HEADERS` keep the API settings separate. Because the root `conftest.py` imports this module, both groups are required even when collecting or running only one test file.

### Run tests

`pytest.ini` adds `-v` to every run, so the commands below print one line per test case.

Collect tests without sending HTTP requests:

```bash
pytest --collect-only
```

Run only the persistent lifecycle:

```bash
pytest test_products.py::test_product_lifecycle
```

Run only the three Noble authentication cases (GET requests):

```bash
pytest test_products.py -k authentication
```

Run all four Noble cases, including the lifecycle:

```bash
pytest test_products.py
```

Run the classic tests or the complete suite:

```bash
pytest test_users.py
pytest
```

Run only the smoke set:

```bash
pytest -m smoke
```

The lifecycle creates, updates and deletes a real record. Classic tests also include POST requests. The complete suite is not currently expected to be all green; see the observations below.

## Markers

Custom markers are registered in `pytest.ini`. `--strict-markers` turns an unregistered or misspelled marker into a collection error instead of a silent no-op.

| Marker | Meaning | Tests |
|---|---|---|
| `smoke` | Basic health check: fast, read-only, no data created | `test_noble_authentication_valid_key` |
| `xfail(strict=True, raises=AssertionError)` | Built-in: known failure caused by the observed string POST ID. The test still runs; only an `AssertionError` counts as the expected failure, and an unexpected pass fails the run, signalling that the marker should be removed | `test_create_user_returns_integer_id` |

`smoke` is a custom marker and must be registered; `xfail` and `skip` are built into pytest. `skip` does not run a test and says nothing about the product; `xfail` runs it and reports whether the known failure is still present.

The marker is scoped to the ID-type check only. The other POST checks live in the unmarked `test_create_user_returns_201`. Inside the marked test, the status precondition fails through `pytest.fail()`, whose exception (`Failed`) does not inherit from `AssertionError`, so a wrong status is reported as an ordinary failure rather than as the expected one. The failure message includes the status code and the first 300 characters of the body. A transport error, a non-JSON body or a missing `id` key also raise exceptions outside `raises` and are reported as ordinary failures.

This was verified with three runs of the marked test: unchanged (**XFAIL**), with a deliberately broken path (**FAILED**, `Expected 201, got 404`), and with the expected type temporarily changed to `str` (**FAILED**, `[XPASS(strict)]`). The original code has been restored.

**Known limitation:** the precondition checks the status code, not the endpoint. If the server answers `201` on an unintended path, the marked test can still report XFAIL (see the observations below).

To see skip and xfail reasons in the summary:

```bash
pytest -rxXs
```

## Persistent product lifecycle

The test creates a product with `price: 100`, reads it independently, updates the price to `200`, reads it again, deletes the record, and verifies a final `404` with `error == "record_not_found"`.

Independent GET requests check persistence: a successful mutation response or an echo of submitted values alone is not sufficient evidence. The response envelope separates record metadata (`body["data"]`) from product fields (`record["data"]`); the record ID is a string. After the update, the test checks the new price and the unchanged name, category and stock flag. Timestamp checks cover presence, not their values or progression. The DELETE response is checked for `204` without parsing JSON.

`api_session` uses `scope="function"`: each requesting test gets its own `requests.Session`. The fixture sets headers and `project_id`, yields the client, and closes it through a context manager after the test, including an ordinary assertion failure. Each request supplies its own timeout.

**Closing the client does not delete the product.** DELETE is still part of the test body. A failure before that step can leave a record behind; product cleanup in teardown is not implemented yet.

PATCH is excluded from this scenario. In an earlier manual experiment, its `200` response echoed an update that an independent GET did not find persisted.

## Noble authentication checks

All cases read `/api/collections/products/records` with the same `project_id` and `x-reqres-env`.

| Case | Expected response | Additional checks |
|---|---|---|
| Valid key | 200 | No `error` field; `data` exists and is a list (an empty list is allowed) |
| Invalid key | 403 | `error` exists and equals `invalid_api_key` |
| Missing key | 401 | `error` exists and equals `missing_api_key` |

The successful case uses `api_session`. The two rejection cases share a parametrized test and use direct `requests.get` calls with explicit headers, so the fixture's valid key cannot accidentally authenticate the missing-key case. Success and rejection checks are separate functions; no conditional branch is needed in the assertions.

The rejection check was verified by deliberately breaking an expected status and then an expected error string. Each run failed at the corresponding assertion while the other cases still ran. Correct expectations have been restored.

## Classic users tests

| Test | Current assertions |
|---|---|
| `test_request_without_reqres_api_key_returns_401` | 401, `missing_api_key`, and presence of `message` |
| `test_reqres_api_key_accepted_in_query_param` | 200 and the requested page when the key is supplied in the query |
| `test_get_users_list_returns_requested_page` | 200 and the requested page with header authentication |
| `test_request_with_invalid_reqres_api_key_in_query_returns_403` | 403 and `invalid_api_key` |
| `test_get_single_user_returns_expected_user` | 200, a `data` envelope, integer ID and the requested ID value |
| `test_get_nonexistent_user_returns_404` | 404 with valid authentication supplied |
| `test_create_user_returns_201` | 201, echoed name/job, presence of `createdAt`/`id` |
| `test_create_user_returns_integer_id` | 201 as a precondition, then an integer `id`. Marked `xfail(strict=True, raises=AssertionError)` |
| `test_post_malformed_json_returns_400` | 400 and `invalid_json` for deliberately truncated JSON |

The malformed-body test uses `data=` and an explicit `Content-Type`; other JSON submissions use `json=`.

### Validation and unresolved observations

- On 24 September 2026, the learner reported **4 passed in 2.61s** for all of `test_products.py`: three authentication cases and the lifecycle. This is not a full-suite result.
- On 13 October 2026, the learner reported **1 failed, 7 passed, 1 xfailed** for all of `test_users.py`. The failure is `test_request_without_reqres_api_key_returns_401`, which received `200` (see the next observation); the xfail is the POST ID-type check.
- The complete suite (`pytest` without arguments) has not been rerun after the fixture/configuration refactor.
- An exploratory header-authentication matrix on classic `/api/users` returned `200` and identical demo bodies with valid, invalid and absent keys. Each body identified a read-only demo with `_meta.context == "legacy_success"`. That matrix was moved to Noble. The older classic tests expecting authentication rejection still need review; a successful query-key request alone does not prove the server validated the key.
- Documentation checked on 18 September was inconsistent: the [ReqRes guide](https://reqres.in/llm.txt) described demo endpoints as public, while [OpenAPI](https://reqres.in/openapi.json) declared API-key security for them. Preserve that distinction when reviewing expectations; the observed public demo responses are not sufficient evidence of an authorization bypass.
- The POST ID-type test expects an integer ID but receives a string (for example, `'61'`), while GET returns an integer. The `xfail` reason records this observed difference. A difference from the GET representation alone does not establish a server defect: the endpoint contracts need to be checked separately.
- During a deliberate-break run on 13 October, a POST to `/api/user` (singular) also returned `201` with a string `id`. The demo may accept arbitrary resource names; this has not been investigated yet.

The remaining classic assertions are unchanged pending review. Apart from the POST ID-type test, they have not been marked `xfail`. Earlier manual notes also recorded differences in response envelopes, naming, error fields and documentation links. They are investigation leads, not verified current defects or evidence that a client necessarily crashes.

## Next steps

- review the remaining classic authentication expectations and the POST ID-type expectation against the expected contracts
- check whether the classic demo accepts POST requests to arbitrary resource names
- decide which other tests belong in the smoke set
- add JSON Schema validation
- address product cleanup after a failed lifecycle
- build a separate suite for an API with pagination and filtering
