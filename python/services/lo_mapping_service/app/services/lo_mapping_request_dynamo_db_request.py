import os
from datetime import datetime, timezone
from uuid import uuid4

import boto3
from dotenv import load_dotenv

from app.core.logging_config import logger


class LOMappingRequestDynamoDBRecord:
    """Persists LO mapping request records in DynamoDB."""

    def __init__(self) -> None:
        load_dotenv()
        self.table_name = os.getenv("LO_MAPPING_REQUESTS_TABLE")
        self.aws_region = os.getenv("AWS_REGION")
        self.aws_access_key = os.getenv("ACCESS_KEY")
        self.aws_secret_key = os.getenv("SECRET_KEY")

    def ensure_table_exists(self) -> None:
        if not self.table_name:
            raise ValueError("LO_MAPPING_REQUESTS_TABLE is not set")

        boto_session = self._create_boto_session()
        dynamodb = boto_session.resource("dynamodb", region_name=self.aws_region)
        client  = boto_session.client("dynamodb", region_name=self.aws_region)

        try:
            client.describe_table(TableName=self.table_name)
            logger.info("DynamoDB table %s already exists", self.table_name)
            return
        except client.exceptions.ResourceNotFoundException:
            logger.info("DynamoDB table %s not found. Creating it now.", self.table_name)
            table = dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {"AttributeName": "request_id", "KeyType": "HASH"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "request_id", "AttributeType": "S"},
                    {"AttributeName": "status", "AttributeType": "S"},
                    {"AttributeName": "created_at", "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "status-created_at-index",
                        "KeySchema": [
                            {"AttributeName": "status", "KeyType": "HASH"},
                            {"AttributeName": "created_at", "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                    },
                ],
            )
            table.wait_until_exists()
            logger.info("DynamoDB table %s is ready", self.table_name)

    def create_request(self, course_id: int | str | None, program_id: int | str | None,
                       input_s3_path: str, status: str = "pending",) -> dict[str, str | int | None]:
        if not self.table_name:
            raise ValueError("LO_MAPPING_REQUESTS_TABLE is not set")
        if not input_s3_path:
            raise ValueError("input_s3_path is required")

        item = {
            "request_id": str(uuid4()), # Generate based on datetime to ensure uniqueness
            "course_id": course_id,
            "program_id": program_id,
            "status": status,
            "input_s3_path": input_s3_path,
            "output_s3_path": input_s3_path.replace("batch_inputs", "batch_outputs") + ".out",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            table = self._create_boto_session().resource("dynamodb").Table(self.table_name)
            table.put_item(Item=item)
            logger.info(
                "Created LO mapping request record in DynamoDB for course_id=%s program_id=%s",
                course_id,
                program_id,
            )
            return item
        except Exception as e:
            raise RuntimeError(f"Failed to create LO mapping request record in DynamoDB: {str(e)}") from e

    def _create_boto_session(self) -> boto3.Session:
        if not self.aws_access_key or not self.aws_secret_key or not self.aws_region:
            raise ValueError("AWS credentials or region are not set in environment variables")

        return boto3.Session(
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region,
        )
