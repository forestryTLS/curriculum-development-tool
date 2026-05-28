"""
Starts FastAPI in test mode with LocalStack. Used for E2E tests.
- If LocalStack isn't already running, starts it (and stops it on exit)
- Starts FastAPI on port 8002 with AWS env vars pointed at LocalStack
"""
import atexit
import os
import time

import requests
import uvicorn
from testcontainers.localstack import LocalStackContainer

LOCALSTACK_HEALTH_URL = f"http://127.0.0.1:{LOCALSTACK_PORT}/_localstack/health"
FASTAPI_PORT = 8002
LOCALSTACK_PORT = LOCALSTACK_PORT

TEST_ENV = {
    "AWS_ENDPOINT_URL":                   f"http://127.0.0.1:{LOCALSTACK_PORT}",
    "AWS_REGION":                         "ca-central-1",
    "AWS_ACCESS_KEY_ID":                  "test",
    "AWS_SECRET_ACCESS_KEY":              "test",
    "ACCESS_KEY":                         "test",
    "SECRET_KEY":                         "test",
    "LO_MAPPING_DYNAMODB_REQUESTS_TABLE": "lo-mapping-requests-e2e",
    "BATCH_TRANSFORM_INPUT_S3_BUCKET":    "curriculum-map-e2e-bucket",
    "OUTPUT_S3_URI":                      "s3://curriculum-map-e2e-bucket/output/",
    "DYNAMODB_STATUS_INDEX":              "status-created_at-index",
    "ALLOWED_ORIGINS":                    "http://localhost,http://127.0.0.1",
    "LARAVEL_API_URL":                    "http://127.0.0.1:8000/api/microservices/lo-mapping/ai-suggestions/store",
}


def is_localstack_running() -> bool:
    try:
        return requests.get(LOCALSTACK_HEALTH_URL, timeout=2).status_code == 200
    except requests.RequestException:
        return False


def wait_for_localstack(timeout: int = 60) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_localstack_running():
            return
        time.sleep(1)
    raise RuntimeError(f"LocalStack did not become ready within {timeout}s")


def ensure_localstack_running() -> None:
    if is_localstack_running():
        # Could be running from another service's test
        print(f"[test] LocalStack already running on {LOCALSTACK_PORT}; reusing it")
    else:
        print("[test] Starting LocalStack via testcontainers")
        container = LocalStackContainer(image="localstack/localstack:3.0")
        # Bind to a fixed host port so every consumer hits the same URL.
        container.with_bind_ports(LOCALSTACK_PORT, LOCALSTACK_PORT)
        container.start()
        # We only reach here if LocalStack wasn't already running, 
        # So that means this test started it, so we should stop it on exit.
        atexit.register(container.stop)
        wait_for_localstack()
        print("[test] LocalStack ready on {LOCALSTACK_PORT}")


def ensure_fastapi_port_free() -> None:
    try:
        r = requests.get(f"http://127.0.0.1:{FASTAPI_PORT}/docs", timeout=1)
        if r.status_code < 500:
            raise RuntimeError(
                f"Port {FASTAPI_PORT} already has a service running. "
                "Stop it before starting test mode."
            )
    except (requests.ConnectionError, requests.Timeout):
        pass


def start_fastapi() -> None:
    os.environ.update(TEST_ENV)
    print(f"[test] Starting FastAPI on port {FASTAPI_PORT} (Ctrl+C to stop)")
    config = uvicorn.Config(
        "app.api.routes:app",
        host="127.0.0.1",
        port=FASTAPI_PORT,
        log_level="info",
    )
    uvicorn.Server(config).run()


if __name__ == "__main__":
    ensure_localstack_running()
    ensure_fastapi_port_free()
    start_fastapi()
