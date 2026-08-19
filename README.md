# api-tests-reqres

API test suite in Python for the [ReqRes](https://reqres.in) REST API — written to practise API testing end to end: designing checks, verifying contracts, and turning findings into evidence.

**Stack:** Python 3.14 · `requests` · `pytest` · `python-dotenv`

---

## What this project is for

The goal is not coverage of ReqRes as a product. The goal is to build the habits that matter in API testing:

- assert on the **whole response** — status code, headers and body — not just the status
- assert on **machine-readable error codes**, never on human-readable message text
- assert on **field types**, not only values — a type change breaks strongly typed clients while values still look fine
- keep configuration out of the code and out of version control
- make a failing test produce evidence that can be pasted into a bug report as is

---

## Quick start

```bash
git clone https://github.com/anton-borodin-inr/api-tests-reqres.git
cd api-tests-reqres

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then put your key into .env
pytest -v
```

A free API key is issued at [app.reqres.in/api-keys](https://app.reqres.in/api-keys). The free tier allows 250 requests per day.

### Configuration

| Variable | Meaning |
|---|---|
| `REQRES_API_KEY` | API key, sent in the `x-api-key` header |
| `REQRES_BASE_URL` | Base URL, `https://reqres.in` |

Both are validated at import time. If either is missing or empty, collection stops with an explicit message instead of producing a wall of identical failures — a broken configuration should never look like a broken product.

---

## What is covered

| Test | Checks |
|---|---|
| `test_request_without_api_key_returns_401` | 401 and `error == "missing_api_key"` when no key is sent |
| `test_get_users_list_returns_requested_page_api_in_params` | key accepted as a query parameter |
| `test_get_users_list_returns_requested_page` | key accepted as a header, pagination returns the requested page |
| `test_request_with_invalid_api_key_in_query_returns_403` | behaviour on an invalid key |
| `test_get_single_user_returns_expected_user` | envelope, `id` value and `id` type on a single resource |
| `test_get_nonexistent_user_returns_404` | 404 on a missing resource |
| `test_create_user_returns_201` | 201, echo of the submitted fields, presence of `id` and `createdAt`, **type of `id`** |
| `test_post_malformed_json_returns_400` | 400 and `error == "invalid_json"` on a truncated JSON body |

The malformed-body case is sent through `data=` with a manually set `Content-Type`, since `json=` serialises its argument and cannot produce an invalid payload.

---

## One test fails on purpose

`test_create_user_returns_201` is **red**, and that is the intended result:

```
assert isinstance(body["id"], int)
E   where False = isinstance('143', int)
```

`GET /api/users/2` returns `"id": 2` — a JSON number.
`POST /api/users` returns `"id": "143"` — a JSON string.

Same logical field, two different JSON types depending on the endpoint. In Postman the difference is invisible; a strongly typed client (Swift, Kotlin, C#) fails to deserialise the response and crashes far from the actual cause.

The test is kept red rather than adjusted to match the defect. A test that is bent to fit broken behaviour stops being a test.

---

## Findings

Collected while building the suite. Severity is assessed as if this were a production API.

| # | Finding | Severity |
|---|---|---|
| 1 | `id` is a number on `GET`, a string on `POST` — breaks typed clients | High |
| 2 | API key is accepted in a query parameter, not only in a header — secrets leak into proxy logs, browser history and `Referer` | Medium |
| 3 | An invalid key returns `403`, a missing key returns `401`. Per RFC 9110 both are `401`; a client receiving `403` will not try to refresh its credentials | Medium |
| 4 | The `401` body reports `"error": "missing_api_key"` and `"context": "invalid_key"` at the same time — mutually exclusive diagnoses, so the consumer cannot tell an absent key from a rejected one | Medium |
| 5 | Response envelope is inconsistent: `GET` wraps the payload in `data`, `POST` returns fields flat | Medium |
| 6 | The `401` response has no `WWW-Authenticate` header, which RFC 9110 §15.5.2 requires | Low |
| 7 | Responses from a single API reference five different documentation URLs | Low |
| 8 | Field naming mixes `snake_case` and `camelCase` within the same API | Low |

Not classified: a single non-reproducible response where an unauthenticated request returned `200` instead of `401`. The leading hypothesis is a CDN cache key that does not vary on `x-api-key`. The test is left in place as a detector in case it recurs.

---

## Next steps

- schema validation with `jsonschema` instead of per-field assertions
- shared setup extracted into a `conftest.py` fixture
- `parametrize` for the authentication matrix
- `xfail` marker for the type defect above, so a permanent failure stays visible without becoming noise
- a second suite against a larger API with real pagination and filtering
