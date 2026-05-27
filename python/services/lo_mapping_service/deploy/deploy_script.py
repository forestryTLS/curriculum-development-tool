"""Deploys the LO Mapping Service's AWS Lambda functions and EventBridge rule to AWS.
If a Lambda already exists, its code and configuration are updated
in place instead of failing.

Run this script from the service's virtual env.
The set up for vitual env is described in docs/setup.md

Prerequisites:
    - AWS CLI installed and configured with credentials via `aws configure`
    - IAM execution role exists with the required permissions policies
    - lo_mapping_service/.env at the service root is filled in based on the .env.example template
"""

import json
import sys
import zipfile
from pathlib import Path

import boto3
from pydantic_settings import BaseSettings, SettingsConfigDict

# Can remove SERVICE_ROOT if we limit where we call this script from
SERVICE_ROOT = Path(__file__).resolve().parent.parent
DEPLOY_DIR = SERVICE_ROOT / "deploy"
HANDLERS_DIR = SERVICE_ROOT / "app" / "lambda_handlers"

# Configure here just in case we want to add alternative versions or change names
START_JOB_FN = "start-batch-transform-job"
PROCESS_RESULTS_FN = "process-batch-transform-results"
START_JOB_MODULE = "lambda_handler_start_batch_tranform_job"
PROCESS_RESULTS_MODULE = "lambda_handler_process_batch_transform_inference_results"
EVENTBRIDGE_RULE = "sagemaker-transform-job-state-change"


class DeploySettings(BaseSettings):
    AWS_REGION: str
    LO_MAPPING_DYNAMODB_REQUESTS_TABLE: str
    HF_MODEL_ID: str
    HF_IMAGE_URI: str
    OUTPUT_S3_URI: str
    IAM_ROLE_ARN: str
    LAMBDA_ROLE_ARN: str

    ACCESS_KEY: str = ""
    SECRET_KEY: str = ""
    DYNAMODB_STATUS_INDEX: str = "status-created_at-index"

    model_config = SettingsConfigDict(
        env_file=str(SERVICE_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


def load_settings() -> DeploySettings:
    print("Loading .env...")
    try:
        settings = DeploySettings()
    except Exception as e:
        sys.exit(f"ERROR loading .env: {e}")

    for key in (
        "AWS_REGION",
        "LO_MAPPING_DYNAMODB_REQUESTS_TABLE",
        "DYNAMODB_STATUS_INDEX",
        "HF_MODEL_ID",
        "HF_IMAGE_URI",
        "OUTPUT_S3_URI",
        "IAM_ROLE_ARN",
        "LAMBDA_ROLE_ARN",
    ):
        print(f"  {key} = {getattr(settings, key)}")
    return settings


def zip_handler(module_name: str, dest: Path) -> Path:
    src = HANDLERS_DIR / f"{module_name}.py"
    if not src.exists():
        sys.exit(f"ERROR: handler not found at {src}")
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(src, arcname=src.name)
    print(f"  zipped {src.name} -> {dest}")
    return dest


def zip_handlers() -> list[Path]:
    print("Zipping handlers...")
    return [
        zip_handler(START_JOB_MODULE, DEPLOY_DIR / "start-batch-transform-job.zip"),
        zip_handler(PROCESS_RESULTS_MODULE, DEPLOY_DIR / "process-batch-transform-results.zip"),
    ]


def deploy_lambda(
    lambda_client,
    function_name: str,
    handler_module: str,
    zip_path: Path,
    role_arn: str,
    variables: dict[str, str],
) -> None:
    handler = f"{handler_module}.lambda_handler"
    zip_bytes = zip_path.read_bytes()
    try:
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime="python3.12",
            Role=role_arn,
            Handler=handler,
            Code={"ZipFile": zip_bytes},
            Timeout=300,
            Environment={"Variables": variables},
        )
        print(f"  created {function_name}")
    except lambda_client.exceptions.ResourceConflictException:
        lambda_client.update_function_code(FunctionName=function_name, ZipFile=zip_bytes)
        # update_function_configuration is rejected while a code update is in progress.
        lambda_client.get_waiter("function_updated").wait(FunctionName=function_name)
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Role=role_arn,
            Handler=handler,
            Timeout=300,
            Environment={"Variables": variables},
        )
        print(f"  updated {function_name}")


def deploy_start_job(lambda_client, settings: DeploySettings, zip_path: Path) -> None:
    print(f"Deploying {START_JOB_FN}...")
    variables = {
        "ACCESS_KEY": settings.ACCESS_KEY,
        "SECRET_KEY": settings.SECRET_KEY,
        "IAM_ROLE_ARN": settings.IAM_ROLE_ARN,
        "HF_MODEL_ID": settings.HF_MODEL_ID,
        "HF_IMAGE_URI": settings.HF_IMAGE_URI,
        "HF_TASK": "text-generation",
        "INSTANCE_TYPE": "ml.g5.2xlarge",
        "INSTANCE_COUNT": "1",
        "OUTPUT_S3_URI": settings.OUTPUT_S3_URI,
        "JOB_NAME_PREFIX": "hf-batch-transform",
        "MODEL_NAME_PREFIX": "hf-batch-transform-model",
        "LO_MAPPING_DYNAMODB_REQUESTS_TABLE": settings.LO_MAPPING_DYNAMODB_REQUESTS_TABLE,
        "DYNAMODB_STATUS_INDEX": settings.DYNAMODB_STATUS_INDEX,
    }
    deploy_lambda(lambda_client, START_JOB_FN, START_JOB_MODULE, zip_path,
                  settings.LAMBDA_ROLE_ARN, variables)


def deploy_process_results(lambda_client, settings: DeploySettings, zip_path: Path) -> None:
    print(f"Deploying {PROCESS_RESULTS_FN}...")
    variables = {
        "ACCESS_KEY": settings.ACCESS_KEY,
        "SECRET_KEY": settings.SECRET_KEY,
        "DYNAMODB_TABLE": settings.LO_MAPPING_DYNAMODB_REQUESTS_TABLE,
        "START_JOB_LAMBDA_NAME": START_JOB_FN,
        "STATUS_INDEX": settings.DYNAMODB_STATUS_INDEX,
        "JOB_NAME_PREFIX": "hf-batch-transform",
    }
    deploy_lambda(lambda_client, PROCESS_RESULTS_FN, PROCESS_RESULTS_MODULE, zip_path,
                  settings.LAMBDA_ROLE_ARN, variables)


def log_lambdas(lambda_client) -> None:
    for fn in [START_JOB_FN, PROCESS_RESULTS_FN]:
        cfg = lambda_client.get_function(FunctionName=fn)["Configuration"]
        print(f"  {fn}:")
        print(f"    LastModified = {cfg.get('LastModified')}")
        print(f"    Runtime      = {cfg.get('Runtime')}")
        print(f"    Handler      = {cfg.get('Handler')}")
        print(f"    Role         = {cfg.get('Role')}")
    print("\n")


def setup_eventbridge(events_client, lambda_client, sts_client, region: str | None) -> None:
    print(f"Setting up EventBridge rule '{EVENTBRIDGE_RULE}'...")
    pattern = json.dumps({
        "source": ["aws.sagemaker"],
        "detail-type": ["SageMaker Transform Job State Change"],
    })
    events_client.put_rule(Name=EVENTBRIDGE_RULE, EventPattern=pattern)
    print(f"  rule '{EVENTBRIDGE_RULE}' put")

    lambda_arn = lambda_client.get_function(
        FunctionName=PROCESS_RESULTS_FN
    )["Configuration"]["FunctionArn"]
    events_client.put_targets(
        Rule=EVENTBRIDGE_RULE,
        Targets=[{"Id": "1", "Arn": lambda_arn}],
    )
    print(f"  target -> {lambda_arn}")

    account_id = sts_client.get_caller_identity()["Account"]
    source_arn = f"arn:aws:events:{region}:{account_id}:rule/{EVENTBRIDGE_RULE}"
    # We have to add permission for EventBridge to invoke the Lambda separately after put_targets,
    # eventbridge-invoke doesn't come under the IAM execution role permissions
    # The user running this script must have the permission for lambda:AddPermission
    try:
        lambda_client.add_permission(
            FunctionName=PROCESS_RESULTS_FN,
            StatementId="eventbridge-invoke",
            Action="lambda:InvokeFunction",
            Principal="events.amazonaws.com",
            SourceArn=source_arn,
        )
        print(f"  invoke permission added (source: {source_arn})")
    except lambda_client.exceptions.ResourceConflictException:
        print(f"  invoke permission already present (source: {source_arn})")


def main() -> None:
    print(f"Service root: {SERVICE_ROOT}")
    settings = load_settings()

    session = boto3.Session(region_name=settings.AWS_REGION)
    lambda_client = session.client("lambda")
    events_client = session.client("events")
    sts_client = session.client("sts")

    start_zip, process_zip = zip_handlers()
    deploy_start_job(lambda_client, settings, start_zip)
    deploy_process_results(lambda_client, settings, process_zip)
    log_lambdas(lambda_client)
    setup_eventbridge(events_client, lambda_client, sts_client, settings.AWS_REGION)

    print("\nDone.")


if __name__ == "__main__":
    main()