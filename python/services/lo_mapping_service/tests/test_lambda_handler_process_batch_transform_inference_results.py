import os

import boto3
import pytest
from moto import mock_aws


os.environ.update({
    "ACCESS_KEY": "fake-key",
    "SECRET_KEY": "fake-secret",
    "IAM_ROLE_ARN": "arn:aws:iam::123456789012:role/fake-role",
    "DYNAMODB_TABLE": "requests-table",
    "START_JOB_LAMBDA_NAME": "start-job-lambda",
    "STATUS_INDEX": "status-createdAt-index",
})

from app.lambda_handlers import lambda_handler_process_batch_transform_inference_results


REGION = "ca-central-1"
TABLE_NAME = "requests-table"
GSI_NAME = "status-createdAt-index"


def make_table(dynamodb):
    return dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[{"AttributeName": "request_id", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "request_id", "AttributeType": "S"},
            {"AttributeName": "status", "AttributeType": "S"},
            {"AttributeName": "created_at", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[{
            "IndexName": GSI_NAME,
            "KeySchema": [
                {"AttributeName": "status", "KeyType": "HASH"},
                {"AttributeName": "created_at", "KeyType": "RANGE"},
            ],
            "Projection": {"ProjectionType": "ALL"},
        }],
        BillingMode="PAY_PER_REQUEST",
    )


def put_record(table, request_id, status, created_at, transform_job_name=None,
               course_id="CS101",program_id="PROG1",
               input_s3_path="s3://my-bucket/input/file.jsonl",
               output_s3_path="s3://my-bucket/output/file.jsonl.out",
               ):
    item = {
        "request_id": request_id,
        "status": status,
        "created_at": created_at,
        "course_id": course_id,
        "program_id": program_id,
        "input_s3_path": input_s3_path,
        "output_s3_path": output_s3_path,
    }
    if transform_job_name:
        item["transform_job_name"] = transform_job_name
    table.put_item(Item=item)


@pytest.fixture(autouse=True)
def aws_mocks():
    with mock_aws():
        lambda_handler_process_batch_transform_inference_results.dynamodb = boto3.resource(
            "dynamodb",
            region_name=REGION,
        )
        lambda_handler_process_batch_transform_inference_results.lambda_client = boto3.client(
            "lambda",
            region_name=REGION,
        )
        yield


def test_missing_job_name_or_status_returns_400():
    resp = lambda_handler_process_batch_transform_inference_results.lambda_handler(
        {"detail": {}},
        None,
    )

    assert resp["statusCode"] == 400
    assert resp["body"] == "Invalid EventBridge event."


def test_no_matching_in_progress_record_returns_404():
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    make_table(dynamodb)

    resp = lambda_handler_process_batch_transform_inference_results.lambda_handler(
        {
            "detail": {
                "TransformJobName": "hf-batch-transform-course-CS101-program-PROG1-123",
                "TransformJobStatus": "Completed",
            }
        },
        None,
    )

    assert resp["statusCode"] == 404
    assert (resp["body"]
        == "No IN_PROGRESS record found for job 'hf-batch-transform-course-CS101-program-PROG1-123'."
    )


def test_completed_job_updates_status_and_triggers_next_job(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = make_table(dynamodb)
    put_record(
        table,
        "rec-in-progress",
        "IN_PROGRESS",
        "2024-01-01T10:00:00",
        transform_job_name="job-123",
    )
    put_record(table, "rec-pending", "PENDING", "2024-01-01T11:00:00")

    triggered = []
    monkeypatch.setattr(
        lambda_handler_process_batch_transform_inference_results,
        "trigger_start_job_lambda",
        lambda record_id: triggered.append(record_id),
    )

    resp = lambda_handler_process_batch_transform_inference_results.lambda_handler(
        {
            "detail": {
                "TransformJobName": "job-123",
                "TransformJobStatus": "Completed",
            }
        },
        None,
    )

    assert resp["statusCode"] == 200
    assert resp["body"]["processedJob"] == "job-123"
    assert resp["body"]["updatedRecordId"] == "rec-in-progress"
    assert resp["body"]["updatedRecordStatus"] == "AWAITING_COMPLETION"
    assert resp["body"]["nextJobTriggered"] == "rec-pending"
    assert triggered == ["rec-pending"]

    updated = table.get_item(Key={"request_id": "rec-in-progress"})["Item"]
    assert updated["status"] == "AWAITING_COMPLETION"
    assert "updated_at" in updated


def test_failed_job_updates_status_without_triggering_next_job(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = make_table(dynamodb)
    put_record(
        table,
        "rec-in-progress",
        "IN_PROGRESS",
        "2024-01-01T10:00:00",
        transform_job_name="job-456",
    )

    triggered = []
    monkeypatch.setattr(
        lambda_handler_process_batch_transform_inference_results,
        "trigger_start_job_lambda",
        lambda record_id: triggered.append(record_id),
    )

    resp = lambda_handler_process_batch_transform_inference_results.lambda_handler(
        {
            "detail": {
                "TransformJobName": "job-456",
                "TransformJobStatus": "Failed",
            }
        },
        None,
    )

    assert resp["statusCode"] == 200
    assert resp["body"]["processedJob"] == "job-456"
    assert resp["body"]["updatedRecordId"] == "rec-in-progress"
    assert resp["body"]["updatedRecordStatus"] == "AWAITING_COMPLETION_FAILED"
    assert resp["body"]["nextJobTriggered"] is None
    assert triggered == []

    updated = table.get_item(Key={"request_id": "rec-in-progress"})["Item"]
    assert updated["status"] == "AWAITING_COMPLETION_FAILED"
    assert "updated_at" in updated
