from datetime import datetime
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Key

from app.core.config import Settings
from app.core.logging_config import logger


class LOMappingRequestDynamoDBRecord:
    """Persists LO mapping request records in DynamoDB."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.table_name = self.settings.LO_MAPPING_REQUESTS_TABLE
        self.aws_region = self.settings.AWS_REGION
        self.aws_access_key = self.settings.ACCESS_KEY
        self.aws_secret_key = self.settings.SECRET_KEY
        self.status_index = self.settings.DYNAMODB_STATUS_INDEX

    def ensure_table_exists(self):
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

    def create_request(self, course_id, program_id, input_s3_path, status: str = "PENDING",):
        if not self.table_name:
            raise ValueError("LO_MAPPING_REQUESTS_TABLE is not set")
        if not input_s3_path:
            raise ValueError("input_s3_path is required")

        item = {
            "request_id": datetime.now().strftime('%Y%m%d-%H%M%S-') + str(uuid4()), # Generate based on datetime to ensure uniqueness
            "course_id": course_id,
            "program_id": program_id,
            "status": status,
            "input_s3_path": input_s3_path,
            "output_s3_path": input_s3_path.replace("batch_inputs", "batch_outputs") + ".out",
            "created_at": datetime.now().isoformat(),
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

    def get_records_by_status(self, status: str) -> list[dict]:
        """Return all records for a given status using the status-created_at GSI"""
        
        table = self._get_table()
        items = []
        args = {
            "IndexName": self.status_index,
            "KeyConditionExpression": Key("status").eq(status),
        }

        response = table.query(**args)
        items.extend(response.get("Items", []))

        while "LastEvaluatedKey" in response:
            response = table.query(**args, ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))

        return items

    def find_latest_awaiting_record_by_ids(self, course_id, program_id) -> dict | None:
        """Find the latest record for the given course/program awaiting post-processing"""
        
        latest_record = None
        table = self._get_table()

        for status in ("AWAITING_COMPLETION", "AWAITING_COMPLETION_FAILED"):
            response = table.query(
                IndexName=self.status_index,
                KeyConditionExpression=Key("status").eq(status),
            )

            for item in response.get("Items", []):
                if item.get("course_id") != course_id or item.get("program_id") != program_id:
                    continue
                if latest_record is None or item.get("created_at", "") > latest_record.get("created_at", ""):
                    latest_record = item

            while "LastEvaluatedKey" in response:
                response = table.query(
                    IndexName=self.status_index,
                    KeyConditionExpression=Key("status").eq(status),
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                )
                for item in response.get("Items", []):
                    if item.get("course_id") != course_id or item.get("program_id") != program_id:
                        continue
                    if latest_record is None or item.get("created_at", "") > latest_record.get("created_at", ""):
                        latest_record = item

        return latest_record

    def delete_request(self, request_id: str) -> None:
        """Delete a record by its request_id"""
        self._get_table().delete_item(Key={"request_id": request_id})
        logger.info("Deleted LO mapping request record '%s'.", request_id)

    def _create_boto_session(self) -> boto3.Session:
        if not self.aws_access_key or not self.aws_secret_key or not self.aws_region:
            raise ValueError("AWS credentials or region are not set in environment variables")

        return boto3.Session(
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region,
        )

    def _get_table(self):
        if not self.table_name:
            raise ValueError("LO_MAPPING_REQUESTS_TABLE is not set")
        return self._create_boto_session().resource("dynamodb").Table(self.table_name)
