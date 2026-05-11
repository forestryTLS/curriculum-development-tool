"""
Shared configs for E2E tests.

Prerequisites for running these tests (see README.md):
  - Docker running (for LocalStack)
  - Postgres running (the same one Laravel uses)
  - FastAPI service running on $FASTAPI_URL with AWS endpoints pointing at LocalStack
  - Laravel server running on $LARAVEL_URL
  - A test user account exists with credentials $E2E_TEST_USER_EMAIL / $E2E_TEST_USER_PASSWORD
"""
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

import boto3
import psycopg2
import pytest
import requests
from testcontainers.localstack import LocalStackContainer

REGION              = "ca-central-1"
FAKE_AWS_KEY        = "test"
FAKE_AWS_SECRET     = "test"
# Session-unique names so we never collide with leftover resources from a prior run.
_SESSION_TAG        = uuid.uuid4().hex[:8]
DYNAMO_TABLE_NAME   = os.environ.get("E2E_DYNAMO_TABLE",  f"lo-mapping-requests-e2e-{_SESSION_TAG}")
S3_BUCKET           = os.environ.get("E2E_S3_BUCKET",    f"curriculum-map-e2e-bucket-{_SESSION_TAG}")
DYNAMO_GSI          = "status-created_at-index"

LARAVEL_URL         = os.environ.get("LARAVEL_URL", "http://127.0.0.1:8000")
FASTAPI_URL         = os.environ.get("FASTAPI_URL", "http://127.0.0.1:8002")

PG_DSN              = os.environ.get(
    "E2E_PG_DSN",
    "postgresql://root@localhost:5432/laravel",
)

E2E_USER_EMAIL      = os.environ.get("E2E_TEST_USER_EMAIL")
E2E_USER_PASSWORD   = os.environ.get("E2E_TEST_USER_PASSWORD")

# High IDs so tests do not collide with real data. Cleanup deletes by these IDs.
TEST_COURSE_ID      = 99001
TEST_PROGRAM_ID     = 99001
TEST_CLO_IDS        = [99001, 99002]
TEST_PLO_IDS        = [99001, 99002]
TEST_MAP_SCALE_IDS  = [99001, 99002]  # one for "I" (Introduced), one for "D" (Developed)


# ─────────────────── LocalStack ───────────────────

@pytest.fixture(scope="session")
def localstack_container():
    with LocalStackContainer(image="localstack/localstack:3.0") as ls:
        yield ls


@pytest.fixture(scope="session")
def localstack_endpoint(localstack_container):
    return localstack_container.get_url()


@pytest.fixture(scope="session", autouse=True)
def localstack_env(localstack_endpoint):
    """Force boto3 in this process (and child FastAPI requests via env) to LocalStack."""
    overrides = {
        "AWS_ENDPOINT_URL":    localstack_endpoint,
        "AWS_REGION":          REGION,
        "AWS_ACCESS_KEY_ID":   FAKE_AWS_KEY,
        "AWS_SECRET_ACCESS_KEY": FAKE_AWS_SECRET,
    }
    original = {k: os.environ.get(k) for k in overrides}
    os.environ.update(overrides)
    yield
    for k, v in original.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


@pytest.fixture(scope="session")
def boto_session(localstack_endpoint):
    return boto3.Session(
        aws_access_key_id=FAKE_AWS_KEY,
        aws_secret_access_key=FAKE_AWS_SECRET,
        region_name=REGION,
    )


@pytest.fixture(scope="session")
def s3_client(boto_session, localstack_endpoint):
    return boto_session.client("s3", endpoint_url=localstack_endpoint)


@pytest.fixture(scope="session")
def dynamodb_resource(boto_session, localstack_endpoint):
    return boto_session.resource("dynamodb", endpoint_url=localstack_endpoint)


@pytest.fixture(scope="session")
def s3_bucket(s3_client):
    s3_client.create_bucket(
        Bucket=S3_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": REGION},
    )
    yield S3_BUCKET
    objects = s3_client.list_objects_v2(Bucket=S3_BUCKET).get("Contents", [])
    for obj in objects:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=obj["Key"])
    s3_client.delete_bucket(Bucket=S3_BUCKET)


@pytest.fixture
def dynamo_table(fastapi_service, dynamodb_resource):
    """Adopt the table FastAPI's lifespan hook creates; wipe items between tests."""
    table = dynamodb_resource.Table(DYNAMO_TABLE_NAME)
    table.wait_until_exists()
    yield table
    scan = table.scan(ProjectionExpression="request_id")
    with table.batch_writer() as batch:
        for item in scan.get("Items", []):
            batch.delete_item(Key={"request_id": item["request_id"]})


# ─────────────────── Postgres test data ───────────────────

@pytest.fixture(scope="session")
def pg_conn():
    conn = psycopg2.connect(PG_DSN)
    conn.autocommit = False
    yield conn
    conn.close()


@pytest.fixture
def seeded_course_program(pg_conn):
    """
    Set up a minimal course/program with 2 CLOs, 2 PLOs, and 2 mapping scales.
    Cleans up everything at the end.
    """
    cur = pg_conn.cursor()
    try:
        # Mapping scales (I = Introduced, D = Developed)
        cur.execute(
            """
            INSERT INTO mapping_scales (map_scale_id, title, abbreviation, description, colour, created_at, updated_at)
            VALUES
              (%s, 'Introduced', 'I', 'Introduced level', '#aaaaaa', NOW(), NOW()),
              (%s, 'Developed',  'D', 'Developed level',  '#bbbbbb', NOW(), NOW())
            ON CONFLICT (map_scale_id) DO NOTHING
            """,
            TEST_MAP_SCALE_IDS,
        )

        # Course. NOT NULL columns without defaults: course_code, delivery_modality (char(1)),
        # year, semester (char(2)), course_title, assigned, type.
        cur.execute(
            """
            INSERT INTO courses (
                course_id, course_code, course_title,
                delivery_modality, year, semester,
                assigned, type,
                created_at, updated_at
            )
            VALUES (%s, 'E2ETEST', 'E2E Test Course',
                    'O', 2026, 'F1',
                    0, 'Other',
                    NOW(), NOW())
            ON CONFLICT (course_id) DO NOTHING
            """,
            (TEST_COURSE_ID,),
        )

        # Learning outcomes (CLOs)
        for i, lo_id in enumerate(TEST_CLO_IDS, start=1):
            cur.execute(
                """
                INSERT INTO learning_outcomes (l_outcome_id, course_id, l_outcome, clo_shortphrase, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (l_outcome_id) DO NOTHING
                """,
                (lo_id, TEST_COURSE_ID, f"Test CLO {i}", f"clo{i}"),
            )

        # Program
        cur.execute(
            """
            INSERT INTO programs (program_id, program, level, status, created_at, updated_at)
            VALUES (%s, 'E2E Test Program', 'undergrad', 1, NOW(), NOW())
            ON CONFLICT (program_id) DO NOTHING
            """,
            (TEST_PROGRAM_ID,),
        )

        # Program learning outcomes (PLOs)
        for i, plo_id in enumerate(TEST_PLO_IDS, start=1):
            cur.execute(
                """
                INSERT INTO program_learning_outcomes (pl_outcome_id, program_id, pl_outcome, plo_shortphrase, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (pl_outcome_id) DO NOTHING
                """,
                (plo_id, TEST_PROGRAM_ID, f"Test PLO {i}", f"plo{i}"),
            )

        # Link mapping scales to program
        for ms_id in TEST_MAP_SCALE_IDS:
            cur.execute(
                """
                INSERT INTO mapping_scale_programs (program_id, map_scale_id, created_at, updated_at)
                VALUES (%s, %s, NOW(), NOW())
                ON CONFLICT DO NOTHING
                """,
                (TEST_PROGRAM_ID, ms_id),
            )

        cur.execute(
            "DELETE FROM course_programs WHERE course_id = %s AND program_id = %s",
            (TEST_COURSE_ID, TEST_PROGRAM_ID),
        )
        cur.execute(
            """
            INSERT INTO course_programs (course_id, program_id, course_required, manual_map_status, ai_suggestion_status, created_at, updated_at)
            VALUES (%s, %s, 0, false, false, NOW(), NOW())
            """,
            (TEST_COURSE_ID, TEST_PROGRAM_ID),
        )

        # HasAccessMiddleware redirects to /home unless the user owns the course/program.
        email, _ = _resolve_credentials()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
        if row is None:
            raise RuntimeError(
                f"Test login user {email!r} not found in users table. "
                f"Did you run UserSeeder? (php artisan db:seed --class=UserSeeder)"
            )
        test_user_id = row[0]
        cur.execute(
            """
            INSERT INTO course_users (course_id, user_id, permission, created_at, updated_at)
            VALUES (%s, %s, 1, NOW(), NOW())
            """,
            (TEST_COURSE_ID, test_user_id),
        )
        cur.execute(
            """
            INSERT INTO program_users (user_id, program_id, permission, created_at, updated_at)
            VALUES (%s, %s, 1, NOW(), NOW())
            """,
            (test_user_id, TEST_PROGRAM_ID),
        )

        pg_conn.commit()
        yield {
            "course_id":  TEST_COURSE_ID,
            "program_id": TEST_PROGRAM_ID,
            "clo_ids":    TEST_CLO_IDS,
            "plo_ids":    TEST_PLO_IDS,
            "scale_ids":  TEST_MAP_SCALE_IDS,
        }
    finally:
        # If the seed inserts above failed mid-way the transaction is aborted, so
        # any subsequent statement would error with InFailedSqlTransaction. Roll
        # back first so the cleanup deletes can run regardless of how we got here.
        pg_conn.rollback()
        cur.close()
        cur = pg_conn.cursor()
        try:
            cur.execute("DELETE FROM outcome_map_ai_suggestions WHERE l_outcome_id = ANY(%s)", (TEST_CLO_IDS,))
            cur.execute("DELETE FROM outcome_maps WHERE l_outcome_id = ANY(%s)", (TEST_CLO_IDS,))
            cur.execute("DELETE FROM course_users WHERE course_id = %s", (TEST_COURSE_ID,))
            cur.execute("DELETE FROM program_users WHERE program_id = %s", (TEST_PROGRAM_ID,))
            cur.execute("DELETE FROM course_programs WHERE course_id = %s AND program_id = %s", (TEST_COURSE_ID, TEST_PROGRAM_ID))
            cur.execute("DELETE FROM mapping_scale_programs WHERE program_id = %s", (TEST_PROGRAM_ID,))
            cur.execute("DELETE FROM program_learning_outcomes WHERE pl_outcome_id = ANY(%s)", (TEST_PLO_IDS,))
            cur.execute("DELETE FROM learning_outcomes WHERE l_outcome_id = ANY(%s)", (TEST_CLO_IDS,))
            cur.execute("DELETE FROM mapping_scales WHERE map_scale_id = ANY(%s)", (TEST_MAP_SCALE_IDS,))
            cur.execute("DELETE FROM programs WHERE program_id = %s", (TEST_PROGRAM_ID,))
            cur.execute("DELETE FROM courses WHERE course_id = %s", (TEST_COURSE_ID,))
            pg_conn.commit()
        finally:
            cur.close()


# ─────────────────── Laravel auth ───────────────────

def _resolve_credentials() -> tuple[str, str]:
    """Returns (email, password); defaults to the seeded admin user, override via env vars."""
    email    = os.environ.get("E2E_TEST_USER_EMAIL")    or "admintest@gmail.com"
    password = os.environ.get("E2E_TEST_USER_PASSWORD") or "password"
    return email, password


@pytest.fixture(scope="session")
def laravel_session():
    """Returns an authenticated requests.Session, or fails loudly if the user can't be used."""
    email, password = _resolve_credentials()

    sess = requests.Session()
    login_page = sess.get(f"{LARAVEL_URL}/login")
    login_page.raise_for_status()
    import re
    m = re.search(r'name="_token"\s+value="([^"]+)"', login_page.text)
    if not m:
        pytest.fail("Could not parse CSRF token from /login page")
    token = m.group(1)

    r = sess.post(
        f"{LARAVEL_URL}/login",
        data={"email": email, "password": password, "_token": token},
        allow_redirects=True,
    )
    if r.status_code >= 400 or "/login" in r.url:
        pytest.fail(f"Login failed for {email!r} — check credentials")

    # This means the user exists but their email hasn't been veified yet
    probe = sess.get(f"{LARAVEL_URL}/home", allow_redirects=True)
    if "/email/verify" in probe.url:
        pytest.fail(
            f"Test user {email!r} is not email-verified — Laravel will redirect every request to /email/verify.\n"
            f"Fix: UPDATE users SET email_verified_at = NOW() WHERE email = '{email}';"
        )

    return sess


def get_csrf_token(sess: requests.Session, page_url: str) -> str:
    """Grab the X-CSRF-TOKEN by GETting any page and parsing the meta tag."""
    import re
    page = sess.get(page_url)
    page.raise_for_status()
    m = re.search(r'name="csrf-token"\s+content="([^"]+)"', page.text)
    return m.group(1) if m else ""


# ─────────────────── FastAPI subprocess ───────────────────

FASTAPI_TEST_PORT = int(os.environ.get("E2E_FASTAPI_PORT", "8002"))


@pytest.fixture(scope="session")
def fastapi_service(localstack_endpoint, s3_bucket):
    """
    Boot the lo_mapping_service FastAPI as a subprocess, configured to use
    LocalStack and the test bucket/table. Yields the base URL. Kills the process
    on teardown.

    Refuses to start if port is already in use (so we don't conflict with a dev
    FastAPI instance).
    """
    try:
        r = requests.get(f"http://127.0.0.1:{FASTAPI_TEST_PORT}/health", timeout=1)
        if r.status_code == 200:
            pytest.fail(
                f"Port {FASTAPI_TEST_PORT} already has a FastAPI service running. "
                f"Stop it before running E2E tests, or set E2E_FASTAPI_PORT to a free port."
            )
    except (requests.ConnectionError, requests.Timeout):
        pass  # Port free, proceed

    service_root = Path(__file__).resolve().parents[2]

    if sys.platform == "win32":
        venv_python = service_root / "env" / "Scripts" / "python.exe"
    else:
        venv_python = service_root / "env" / "bin" / "python"
    if not venv_python.exists():
        raise FileNotFoundError(f"Could not find FastAPI python venv at {venv_python}. Did you run 'python -m venv env' and 'pip install -r requirements.txt'?")

    env = os.environ.copy()
    env.update({
        "AWS_ENDPOINT_URL":                   localstack_endpoint,
        "AWS_REGION":                         REGION,
        "AWS_ACCESS_KEY_ID":                  FAKE_AWS_KEY,
        "AWS_SECRET_ACCESS_KEY":              FAKE_AWS_SECRET,
        "ACCESS_KEY":                         FAKE_AWS_KEY,
        "SECRET_KEY":                         FAKE_AWS_SECRET,
        "LO_MAPPING_DYNAMODB_REQUESTS_TABLE": DYNAMO_TABLE_NAME,
        "BATCH_TRANSFORM_INPUT_S3_BUCKET":    S3_BUCKET,
        "OUTPUT_S3_URI":                      f"s3://{S3_BUCKET}/output/",
        "DYNAMODB_STATUS_INDEX":              DYNAMO_GSI,
        "ALLOWED_ORIGINS":                    "http://localhost,http://127.0.0.1",
        "LARAVEL_API_URL":                    f"{LARAVEL_URL}/api/microservices/lo-mapping/ai-suggestions/store",
    })

    # Dump logs into temp file for debugging
    import tempfile
    log_file = tempfile.NamedTemporaryFile(
        prefix="e2e-fastapi-", suffix=".log", delete=False, mode="w+", encoding="utf-8",
    )
    log_path = Path(log_file.name)

    proc = subprocess.Popen(
        [
            str(venv_python), "-m", "uvicorn", "app.api.routes:app",
            "--host", "127.0.0.1",
            "--port", str(FASTAPI_TEST_PORT),
            "--log-level", "info",
        ],
        env=env,
        cwd=str(service_root),
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True,
    )

    def _read_log() -> str:
        try:
            return log_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return "<could not read FastAPI log>"

    # Wait up to 30s for /health to come up
    base_url = f"http://127.0.0.1:{FASTAPI_TEST_PORT}"
    health_url = f"{base_url}/health"
    deadline = time.time() + 30
    while time.time() < deadline:
        if proc.poll() is not None:
            pytest.fail(f"FastAPI exited early during startup:\n{_read_log()}")
        try:
            if requests.get(health_url, timeout=1).status_code == 200:
                break
        except (requests.ConnectionError, requests.Timeout):
            pass
        time.sleep(0.5)
    else:
        proc.terminate()
        pytest.fail(f"FastAPI never became ready on {base_url}:\n{_read_log()}")

    print(f"\n[e2e] FastAPI log: {log_path}")
    yield base_url

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    log_file.close()
    # Always print the FastAPI log at teardown so failing tests have evidence.
    print(f"\n[e2e] FastAPI subprocess log ({log_path}):\n{_read_log()}")


# ─────────────────── Helpers ───────────────────

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def upload_dummy_sagemaker_output(s3_client, bucket: str, key: str) -> str:
    # Returns S3-formatted output from sample_ai_output.jsonl
    with open(FIXTURES_DIR / "sample_ai_output.jsonl", "rb") as f:
        s3_client.put_object(Bucket=bucket, Key=key, Body=f.read())
    return f"s3://{bucket}/{key}"
