# test_lambda.py
import json
import os
import pytest
import boto3
from datetime import datetime
from moto import mock_aws
from unittest.mock import patch

########### Set all required env vars BEFORE and helpers ######################
os.environ.update({
    "ACCESS_KEY":                          "fake-key",
    "SECRET_KEY":                          "fake-secret",
    "IAM_ROLE_ARN":                        "arn:aws:iam::123456789012:role/fake-role",
    "HF_MODEL_ID":                         "Qwen3",
    "HF_IMAGE_URI":                        "123456789.dkr.ecr.ca-central-1.amazonaws.com/huggingface-pytorch-tgi-inference:2.1.1-tgi2.0.0-gpu-py310-cu121-ubuntu22.04",
    "INPUT_S3_URI":                        "s3://my-bucket/input/",
    "OUTPUT_S3_URI":                       "s3://my-bucket/output/",
    "LO_MAPPING_DYNAMODB_REQUESTS_TABLE":  "requests-table",
    "DYNAMODB_STATUS_INDEX":               "status-createdAt-index",
})

from app.lambda_handlers import lambda_handler_start_batch_tranform_job


REGION = "ca-central-1"
TABLE_NAME = "requests-table"
GSI_NAME = "status-createdAt-index"


def make_table(dynamodb):
    """Create the DynamoDB table + GSI that the Lambda expects."""
    return dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[{"AttributeName": "request_id", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "request_id", "AttributeType": "S"},
            {"AttributeName": "status",     "AttributeType": "S"},
            {"AttributeName": "created_at", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[{
            "IndexName": GSI_NAME,
            "KeySchema": [
                {"AttributeName": "status",     "KeyType": "HASH"},
                {"AttributeName": "created_at", "KeyType": "RANGE"},
            ],
            "Projection": {"ProjectionType": "ALL"},
        }],
        BillingMode="PAY_PER_REQUEST",
    )


def put_record(table, request_id, status, created_at,
               course_id="CS101", program_id="PROG1",
               input_s3_path="s3://my-bucket/input/file.jsonl"):
    table.put_item(Item={
        "request_id":    request_id,
        "status":        status,
        "created_at":    created_at,
        "course_id":     course_id,
        "program_id":    program_id,
        "input_s3_path": input_s3_path,
    })
    
@pytest.fixture(autouse=True)
def aws_mocks():
    with mock_aws():
        lambda_handler_start_batch_tranform_job.sagemaker_client = boto3.Session(region_name="ca-central-1").client("sagemaker")
        lambda_handler_start_batch_tranform_job.dynamodb_resource = boto3.resource("dynamodb", region_name="ca-central-1")
        yield

########### Tests ##########################################################################

@mock_aws
def test_missing_record_id_returns_400():
    resp = lambda_handler_start_batch_tranform_job.lambda_handler({}, None)
    assert resp["statusCode"] == 400
    assert "Missing 'record_id' in event." == resp["body"]["error"]


@mock_aws
def test_record_not_found_returns_404():
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    make_table(dynamodb)

    resp = lambda_handler_start_batch_tranform_job.lambda_handler({"record_id": "nonexistent"}, None)
    assert resp["statusCode"] == 404
    assert "Record with request_id 'nonexistent' not found." == resp["body"]["error"]


@mock_aws
def test_record_not_pending_returns_404():
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = make_table(dynamodb)
    put_record(table, "rec-1", "IN_PROGRESS", "2024-01-01T10:00:00")

    resp = lambda_handler_start_batch_tranform_job.lambda_handler({"record_id": "rec-1"}, None)
    assert resp["statusCode"] == 404
    assert "Record with request_id 'rec-1' is not PENDING (status: IN_PROGRESS). No action taken." == resp["body"]["error"]


@mock_aws
def test_job_launched_for_triggered_record():
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = make_table(dynamodb)
    put_record(table, "rec-1", "PENDING", "2024-01-01T10:00:00")

    resp = lambda_handler_start_batch_tranform_job.lambda_handler({"record_id": "rec-1"}, None)

    assert resp["statusCode"] == 200
    body = resp["body"]
    assert body["startedForRecordId"] == "rec-1"
    assert body["triggeredByRecordId"] == "rec-1"
    assert "Batch Transform job submitted." == body["message"]
    assert "hf-batch-transform-course-CS101-program-PROG1-" in body["jobName"]

    updated = table.get_item(Key={"request_id": "rec-1"})["Item"]
    assert updated["status"] == "IN_PROGRESS"
    assert updated["transform_job_name"] == body["jobName"]
    assert "updated_at" in updated


@mock_aws
def test_older_pending_record_is_prioritised():
    """If an older PENDING record exists, that one's job should be started."""
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = make_table(dynamodb)

    put_record(table, "rec-old", "PENDING", "2024-01-01T08:00:00")  # older
    put_record(table, "rec-new", "PENDING", "2024-01-01T10:00:00")  # triggered

    resp = lambda_handler_start_batch_tranform_job.lambda_handler({"record_id": "rec-new"}, None)

    assert resp["statusCode"] == 200
    body = resp["body"]
    assert body["startedForRecordId"] == "rec-old"   # older one would be picked
    assert body["triggeredByRecordId"] == "rec-new"
    assert "Batch Transform job submitted." == body["message"]

    old_item = table.get_item(Key={"request_id": "rec-old"})["Item"]
    new_item = table.get_item(Key={"request_id": "rec-new"})["Item"]
    assert old_item["status"] == "IN_PROGRESS"
    assert new_item["status"] == "PENDING"  


@mock_aws
def test_existing_running_job_blocks_new_launch(monkeypatch):
    """If a transform job is already running, the Lambda should do nothing."""
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = make_table(dynamodb)
    put_record(table, "rec-1", "PENDING", "2024-01-01T10:00:00")

    # Patch a running job so get_running_transform_job returns it
    monkeypatch.setattr(
        lambda_handler_start_batch_tranform_job,
        "get_running_transform_job",
        lambda: {
            "TransformJobName": "hf-batch-transform-already-running",
            "TransformJobStatus": "InProgress",
        },
    )
    
    resp = lambda_handler_start_batch_tranform_job.lambda_handler({"record_id": "rec-1"}, None)
    #print("Lambda response:", resp)
    assert resp["statusCode"] == 200
    assert "Transform job already running. No action taken." == resp["body"]["message"]
    assert "hf-batch-transform-already-running" == resp["body"]["existingJob"]
    # Record should still be PENDING
    item = table.get_item(Key={"request_id": "rec-1"})["Item"]
    assert item["status"] == "PENDING"