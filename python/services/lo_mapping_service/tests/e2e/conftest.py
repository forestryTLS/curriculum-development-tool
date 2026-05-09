"""
Shared fixtures for E2E tests.

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
from pathlib import Path

import boto3
import psycopg2
import pytest
import requests
from testcontainers.localstack import LocalStackContainer

REGION              = "ca-central-1"
FAKE_AWS_KEY        = "test"
FAKE_AWS_SECRET     = "test"
DYNAMO_TABLE_NAME   = os.environ.get("E2E_DYNAMO_TABLE", "lo-mapping-requests-e2e")
S3_BUCKET           = os.environ.get("E2E_S3_BUCKET", "curriculum-map-e2e-bucket")
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
def dynamo_table(dynamodb_resource):
    """Create a fresh DynamoDB table per test."""
    table = dynamodb_resource.create_table(
        TableName=DYNAMO_TABLE_NAME,
        KeySchema=[{"AttributeName": "request_id", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "request_id", "AttributeType": "S"},
            {"AttributeName": "status",     "AttributeType": "S"},
            {"AttributeName": "created_at", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
        GlobalSecondaryIndexes=[{
            "IndexName": DYNAMO_GSI,
            "KeySchema": [
                {"AttributeName": "status",     "KeyType": "HASH"},
                {"AttributeName": "created_at", "KeyType": "RANGE"},
            ],
            "Projection": {"ProjectionType": "ALL"},
        }],
    )
    table.wait_until_exists()
    yield table
    table.delete()


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
    Seed a minimal course/program with 2 CLOs, 2 PLOs, and 2 mapping scales.
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
            VALUES (%s, 'E2E Test Program', 'undergrad', 'active', NOW(), NOW())
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

        # course_programs pivot
        cur.execute(
            """
            INSERT INTO course_programs (course_id, program_id, course_required, manual_map_status, ai_suggestion_status, created_at, updated_at)
            VALUES (%s, %s, false, false, false, NOW(), NOW())
            ON CONFLICT (course_id, program_id) DO UPDATE SET manual_map_status = false, ai_suggestion_status = false
            """,
            (TEST_COURSE_ID, TEST_PROGRAM_ID),
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

def _resolve_credentials() -> tuple[str | None, str | None]:
    """Read credentials from env, or prompt interactively if stdin is a TTY."""
    # Read env fresh at call time, not module-import time, so changes after
    # collection (or weird import-order issues) still get picked up.
    email    = os.environ.get("E2E_TEST_USER_EMAIL")
    password = os.environ.get("E2E_TEST_USER_PASSWORD")

    if email and password:
        return email, password

    if not sys.stdin.isatty():
        return email, password  # caller decides what to do (skip)

    from getpass import getpass
    if not email:
        email = input("Laravel test user email: ").strip()
    if not password:
        password = getpass("Laravel test user password: ")
    return email, password


@pytest.fixture(scope="session")
def laravel_session():
    """Login to Laravel and return a requests.Session with auth cookies + CSRF token helper."""
    email, password = _resolve_credentials()
    if not email or not password:
        pytest.skip(
            "E2E_TEST_USER_EMAIL and E2E_TEST_USER_PASSWORD not set, and stdin is not a TTY. "
            "Either set the env vars, or run pytest with -s to enable interactive prompts."
        )

    sess = requests.Session()
    # GET login page to grab CSRF token
    login_page = sess.get(f"{LARAVEL_URL}/login")
    login_page.raise_for_status()
    import re
    m = re.search(r'name="_token"\s+value="([^"]+)"', login_page.text)
    if not m:
        pytest.skip("Could not parse CSRF token from /login page")
    token = m.group(1)

    # POST credentials
    r = sess.post(
        f"{LARAVEL_URL}/login",
        data={"email": email, "password": password, "_token": token},
        allow_redirects=True,
    )
    if r.status_code >= 400 or "/login" in r.url:
        pytest.skip("Login failed - check credentials")

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
    FastAPI instance the user has running).
    """
    # Refuse to clobber a dev FastAPI instance.
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
        # Fall back to whatever python is on PATH
        venv_python = Path(sys.executable)

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

    proc = subprocess.Popen(
        [
            str(venv_python), "-m", "uvicorn", "app.api.routes:app",
            "--host", "127.0.0.1",
            "--port", str(FASTAPI_TEST_PORT),
            "--log-level", "info",
        ],
        env=env,
        cwd=str(service_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Wait up to 30s for /health to come up
    base_url = f"http://127.0.0.1:{FASTAPI_TEST_PORT}"
    health_url = f"{base_url}/health"
    deadline = time.time() + 30
    while time.time() < deadline:
        if proc.poll() is not None:
            output = proc.stdout.read() if proc.stdout else ""
            pytest.fail(f"FastAPI exited early during startup:\n{output}")
        try:
            if requests.get(health_url, timeout=1).status_code == 200:
                break
        except (requests.ConnectionError, requests.Timeout):
            pass
        time.sleep(0.5)
    else:
        proc.terminate()
        output = proc.stdout.read() if proc.stdout else ""
        pytest.fail(f"FastAPI never became ready on {base_url}:\n{output}")

    yield base_url

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


# ─────────────────── Helpers ───────────────────

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def upload_dummy_sagemaker_output(s3_client, bucket: str, key: str) -> str:
    """Upload the canned AI output JSONL to S3, return s3:// URI."""
    with open(FIXTURES_DIR / "sample_ai_output.jsonl", "rb") as f:
        s3_client.put_object(Bucket=bucket, Key=key, Body=f.read())
    return f"s3://{bucket}/{key}"
