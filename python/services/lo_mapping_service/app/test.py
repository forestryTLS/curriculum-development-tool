"""
Similar to main.py, but points AWS env vars at LocalStack. Used for E2E tests.
If LocalStack isn't already running, starts it (and stops it on exit)
"""
import atexit
import os
import time

import boto3
import requests
import uvicorn
from dotenv import load_dotenv

from testcontainers.localstack import LocalStackContainer
from testcontainers.core.waiting_utils import wait_for_logs

FASTAPI_PORT = 8002
LOCALSTACK_PORT = 4566
LOCALSTACK_HEALTH_URL = f"http://127.0.0.1:{LOCALSTACK_PORT}/_localstack/health"

TEST_ENV = {
    "AWS_ENDPOINT_URL":                   f"http://127.0.0.1:{LOCALSTACK_PORT}",
    "AWS_ACCESS_KEY_ID":                  "test",
    "AWS_SECRET_ACCESS_KEY":              "test",
    "ACCESS_KEY":                         "test",
    "SECRET_KEY":                         "test",
    "ENABLE_TEST_ENDPOINTS":              "true",
}

def is_localstack_running() -> bool:
    try:
        return requests.get(LOCALSTACK_HEALTH_URL, timeout=2).status_code == 200
    except requests.RequestException:
        return False

def ensure_localstack_running():
    if is_localstack_running(): # Could be running from another service's test
        print(f"[test] LocalStack already running on {LOCALSTACK_PORT}; reusing it")
    else:
        print("[test] Starting LocalStack container")
        container = LocalStackContainer(image="localstack/localstack:3.0")
        container.with_bind_ports(LOCALSTACK_PORT, LOCALSTACK_PORT)
        container.start()
        
        atexit.register(container.stop) # If this test started the LocalStack container, stop it on exit
        
        wait_for_logs(container, r"Ready\.", timeout=60)
        print(f"[test] LocalStack ready on {LOCALSTACK_PORT}")

def initialize_db_and_storage():
    """Create the DynamoDB table and S3 bucket the service uses, in
    LocalStack. Doesn't modify existing resources"""
    load_dotenv()
    os.environ.update(TEST_ENV)

    region = os.environ.get("AWS_REGION", "ca-central-1")

    bucket = os.environ.get("BATCH_TRANSFORM_INPUT_S3_BUCKET")
    if not bucket:
        raise RuntimeError("BATCH_TRANSFORM_INPUT_S3_BUCKET is not set in .env")

    s3 = boto3.client(
        "s3",
        endpoint_url=f"http://127.0.0.1:{LOCALSTACK_PORT}",
        region_name=region,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    try:
        s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={"LocationConstraint": region},
        )
        print(f"[test] Created S3 bucket {bucket}")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"[test] S3 bucket {bucket} already exists, reusing")

    from app.services import LOMappingRequestDynamoDBRecord
    LOMappingRequestDynamoDBRecord().ensure_table_exists()


def start_fastapi():
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
    initialize_db_and_storage()
    start_fastapi()
