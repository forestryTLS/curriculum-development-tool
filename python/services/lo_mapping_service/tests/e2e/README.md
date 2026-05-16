# Note: this documentation was compiled by an AI Tool

# E2E Tests for the AI Suggestion Pipeline

- **LocalStack DynamoDB + S3** read/write by FastAPI
- **FastAPI** `process_records` pipeline (S3 read, parse, deliver to Laravel)
- **Laravel** `storeAiSuggestions` controller (writes rows, flips `manual_map_status` and `ai_suggestion_status`)
- **Postgres** `outcome_map_ai_suggestions` rows
- **Step 5 HTML** rendering (purple icons in the right cells)

## Prerequisites

Each of these must be running before invoking pytest:

| Service | How to start | Default URL/DSN |
|---|---|---|
| Docker | OS-dependent | for LocalStack via testcontainers |
| Postgres | OS-dependent | `postgresql://root@localhost:5432/laravel` |
| Laravel | `php artisan serve` from `laravel/` | `http://127.0.0.1:8000` |

**Important: stop your dev FastAPI before running tests.** The test fixture spawns its own FastAPI subprocess on port 8002 with LocalStack-pointing env vars. If a dev FastAPI is already on that port, the test fails fast with a clear message. Override the test port with `E2E_FASTAPI_PORT` if needed.

You can override URLs and the Postgres DSN via env vars:
```
LARAVEL_URL          (default http://127.0.0.1:8000)
E2E_FASTAPI_PORT     (default 8002 - port the test FastAPI binds to)
E2E_PG_DSN           (default postgresql://root@localhost:5432/laravel)
E2E_DYNAMO_TABLE     (default lo-mapping-requests-e2e)
E2E_S3_BUCKET        (default curriculum-map-e2e-bucket)
```

You also need a Laravel test user account for authentication. Set:
```
E2E_TEST_USER_EMAIL=<email>
E2E_TEST_USER_PASSWORD=<password>
```

If these are unset, pytest prompts for them at the start of the session. Run pytest with `-s` to keep stdin connected for the prompt:

```powershell
pytest tests/e2e -v -s
```

## Run

```powershell
cd python/services/lo_mapping_service
pip install -r tests/e2e/requirements.txt
pytest tests/e2e -v
```

The first run takes a while because testcontainers pulls the LocalStack Docker image.

## Test isolation (E2E vs unit tests)

Unit tests under `tests/test_*.py` use `moto` (`@mock_aws`); these E2E tests use LocalStack. To keep the two from clashing in a single pytest session, E2E fixtures route boto3 to LocalStack by passing `endpoint_url=` explicitly on every client/resource, and by injecting `AWS_ENDPOINT_URL` into the FastAPI subprocess via its own env dict. Do not set `AWS_ENDPOINT_URL` on the host `os.environ` — moto only intercepts the standard AWS URLs, so a leaked LocalStack endpoint would silently redirect unit-test boto3 calls at LocalStack.

## Test data

A high-ID-range test course/program is created and torn down per test. IDs used:
- `course_id = 99001`
- `program_id = 99001`
- `l_outcome_id` 99001-99002
- `pl_outcome_id` 99001-99002
- `map_scale_id` 99001-99002

If a previous run failed mid-test, run the cleanup script:

```powershell
python tests/e2e/cleanup.py
```

It deletes the high-ID test rows (99001) in dependency order. The script is idempotent — safe to run anytime.