# Note: this documentation was compiled by an AI Tool

# Lambda Deployment Guide

End-to-end PowerShell commands to deploy both Lambda functions for the lo_mapping_service.

## Prerequisites

- AWS CLI installed and configure`d (`aws configure`).
- Your IAM user has permissions for `lambda:CreateFunction`, `lambda:UpdateFunctionCode`, `lambda:UpdateFunctionConfiguration`, `lambda:GetFunction`, plus `events:PutRule`, `events:PutTargets`, and `lambda:AddPermission` if you are wiring EventBridge.
- An IAM execution role exists for the Lambda. Its trust policy must allow **both** `lambda.amazonaws.com` (so Lambda can run as the role) and `sagemaker.amazonaws.com` (so SageMaker can be passed the same role for batch transform), and the role must have runtime permissions on DynamoDB, S3, SageMaker, CloudWatch Logs, and `lambda:InvokeFunction` on the second Lambda. The role ARN goes in your `.env` as `IAM_ROLE_ARN` (used both as the Lambda's own execution role and as the role passed to SageMaker).
- The `.env` file for the service is filled in with all required values. Confirm there are no inline comments after any value (PowerShell's `.env` parser does not strip them by default).
- A Lambda execution role ARN, which we refer to as `$ROLE_ARN` below. This may be the same as `IAM_ROLE_ARN` if a single role is used for both purposes.

## 0. Set the project root

Run all commands from the service root directory (`python/services/lo_mapping_service/`). All paths below are relative to that. Set `$ROOT` once at the start of your session:

```powershell
# Adjust if your working directory is different
$ROOT     = (Get-Location).Path
$DEPLOY   = "$ROOT\deploy"
$HANDLERS = "$ROOT\app\lambda_handlers"
```

## 1. Load env vars and set PowerShell variables

```powershell
# Load all .env values into the current PowerShell session
$ENV_FILE = "$ROOT\.env"
Get-Content $ENV_FILE | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=([^#]*)') {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
    }
}

# Lambda execution role ARN. Keep this out of .env unless you also want it for runtime use.
$ROLE_ARN = "<paste-the-lambda-execution-role-arn-here>"

# Pull values out of env into PowerShell variables for easy reference
$REGION         = $env:AWS_REGION
$ACCESS_KEY     = $env:ACCESS_KEY
$SECRET_KEY     = $env:SECRET_KEY
$TABLE_NAME     = $env:LO_MAPPING_DYNAMODB_REQUESTS_TABLE
$STATUS_INDEX   = $env:DYNAMODB_STATUS_INDEX
$HF_MODEL_ID    = $env:HF_MODEL_ID
$HF_IMAGE_URI   = $env:HF_IMAGE_URI
$OUTPUT_S3_URI  = $env:OUTPUT_S3_URI
$SAGEMAKER_ROLE = $env:IAM_ROLE_ARN
```

Verify the values loaded:

```powershell
Write-Host "REGION:         $REGION"
Write-Host "TABLE_NAME:     $TABLE_NAME"
Write-Host "HF_MODEL_ID:    $HF_MODEL_ID"
Write-Host "SAGEMAKER_ROLE: $SAGEMAKER_ROLE"
Write-Host "ROLE_ARN:       $ROLE_ARN"
```

If any are blank, that value is missing from `.env` (or `$ROLE_ARN` was not set).

## 2. Zip both Lambda handlers

```powershell
Compress-Archive -Path "$HANDLERS\lambda_handler_start_batch_tranform_job.py" `
  -DestinationPath "$DEPLOY\start-batch-transform-job.zip" -Force

Compress-Archive -Path "$HANDLERS\lambda_handler_process_batch_transform_inference_results.py" `
  -DestinationPath "$DEPLOY\process-batch-transform-results.zip" -Force
```

## 3. Deploy `start-batch-transform-job` Lambda

Build the env JSON in memory, write to a temp file (NOT the project), deploy, delete:

```powershell
$tmpFile = [System.IO.Path]::GetTempFileName()
$json = [PSCustomObject]@{
    Variables = [PSCustomObject]@{
        ACCESS_KEY                         = $ACCESS_KEY
        SECRET_KEY                         = $SECRET_KEY
        IAM_ROLE_ARN                       = $SAGEMAKER_ROLE
        HF_MODEL_ID                        = $HF_MODEL_ID
        HF_IMAGE_URI                       = $HF_IMAGE_URI
        HF_TASK                            = "text-generation"
        INSTANCE_TYPE                      = "ml.g5.2xlarge"
        INSTANCE_COUNT                     = "1"
        OUTPUT_S3_URI                      = $OUTPUT_S3_URI
        JOB_NAME_PREFIX                    = "hf-batch-transform"
        MODEL_NAME_PREFIX                  = "hf-batch-transform-model"
        LO_MAPPING_DYNAMODB_REQUESTS_TABLE = $TABLE_NAME
        DYNAMODB_STATUS_INDEX              = $STATUS_INDEX
    }
} | ConvertTo-Json -Depth 3 -Compress

[System.IO.File]::WriteAllText($tmpFile, $json, (New-Object System.Text.UTF8Encoding $false))

aws lambda create-function `
  --function-name start-batch-transform-job `
  --runtime python3.12 `
  --role $ROLE_ARN `
  --handler lambda_handler_start_batch_tranform_job.lambda_handler `
  --zip-file fileb://$DEPLOY\start-batch-transform-job.zip `
  --region $REGION `
  --timeout 300 `
  --environment file://$tmpFile

Remove-Item $tmpFile
```

## 4. Deploy `process-batch-transform-results` Lambda

```powershell
$tmpFile = [System.IO.Path]::GetTempFileName()
$json = [PSCustomObject]@{
    Variables = [PSCustomObject]@{
        ACCESS_KEY            = $ACCESS_KEY
        SECRET_KEY            = $SECRET_KEY
        DYNAMODB_TABLE        = $TABLE_NAME
        START_JOB_LAMBDA_NAME = "start-batch-transform-job"
        STATUS_INDEX          = $STATUS_INDEX
        JOB_NAME_PREFIX       = "hf-batch-transform"
    }
} | ConvertTo-Json -Depth 3 -Compress

[System.IO.File]::WriteAllText($tmpFile, $json, (New-Object System.Text.UTF8Encoding $false))

aws lambda create-function `
  --function-name process-batch-transform-results `
  --runtime python3.12 `
  --role $ROLE_ARN `
  --handler lambda_handler_process_batch_transform_inference_results.lambda_handler `
  --zip-file fileb://$DEPLOY\process-batch-transform-results.zip `
  --region $REGION `
  --timeout 300 `
  --environment file://$tmpFile

Remove-Item $tmpFile
```

## 5. Verify both Lambdas exist

```powershell
aws lambda get-function --function-name start-batch-transform-job --region $REGION
aws lambda get-function --function-name process-batch-transform-results --region $REGION
```

Both should return JSON with `Configuration` blocks.

## 6. Wire EventBridge to invoke `process-batch-transform-results`

The second Lambda is triggered by EventBridge when SageMaker batch transform jobs change state. Create the EventBridge rule:

```powershell
# Pull your AWS account ID from STS so we don't hardcode it
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)

# PowerShell strips inner double quotes when passing string vars to native executables,
# so we write the pattern to a temp file and use file:// instead.
$tmpPattern = [System.IO.Path]::GetTempFileName()
$pattern = '{"source":["aws.sagemaker"],"detail-type":["SageMaker Transform Job State Change"]}'
[System.IO.File]::WriteAllText($tmpPattern, $pattern, (New-Object System.Text.UTF8Encoding $false))

aws events put-rule `
  --name sagemaker-transform-job-state-change `
  --event-pattern file://$tmpPattern `
  --region $REGION

Remove-Item $tmpPattern

# Get the Lambda ARN
$LAMBDA_ARN = (aws lambda get-function --function-name process-batch-transform-results --region $REGION --query 'Configuration.FunctionArn' --output text)

# Add the Lambda as a target of the rule
aws events put-targets `
  --rule sagemaker-transform-job-state-change `
  --targets "Id=1,Arn=$LAMBDA_ARN" `
  --region $REGION

# Allow EventBridge to invoke the Lambda
aws lambda add-permission `
  --function-name process-batch-transform-results `
  --statement-id eventbridge-invoke `
  --action lambda:InvokeFunction `
  --principal events.amazonaws.com `
  --source-arn "arn:aws:events:${REGION}:${ACCOUNT_ID}:rule/sagemaker-transform-job-state-change" `
  --region $REGION
```

## Re-deploys

If you need to update an existing Lambda's code or env vars, use `update-function-code` and `update-function-configuration` instead of `create-function`. Do NOT use `create-function`, it will fail because the function already exists.

```powershell
# Update code only (no env var change)
Compress-Archive -Path "$HANDLERS\lambda_handler_start_batch_tranform_job.py" `
  -DestinationPath "$DEPLOY\start-batch-transform-job.zip" -Force

aws lambda update-function-code `
  --function-name start-batch-transform-job `
  --zip-file fileb://$DEPLOY\start-batch-transform-job.zip `
  --region $REGION

# Update env vars only (re-build $tmpFile first as in step 3 or 4)
aws lambda update-function-configuration `
  --function-name start-batch-transform-job `
  --environment file://$tmpFile `
  --region $REGION
```

### Verify the deploy actually took effect

It is easy to get a "success" exit code from the Compress-Archive + update-function-code chain even when the deployed code is not what you expect (for example, if `$HANDLERS` was not set in the current shell). Always confirm with:

```powershell
aws lambda get-function `
  --function-name <FUNCTION_NAME> `
  --region $REGION `
  --query "Configuration.LastModified"
```

`LastModified` should match the time you ran the update (within a few seconds). If it shows an older timestamp, the deploy did not actually go through.

You can also invoke the Lambda directly with a synthetic test event to confirm logic changes are in effect:

```powershell
$tmpEvent = [System.IO.Path]::GetTempFileName()
'{"detail":{"TransformJobName":"test-fake-job","TransformJobStatus":"InProgress"}}' |
  Out-File -FilePath $tmpEvent -Encoding ascii -NoNewline

aws lambda invoke `
  --function-name process-batch-transform-results `
  --payload file://$tmpEvent `
  --cli-binary-format raw-in-base64-out `
  --region $REGION `
  response.json

Get-Content response.json
Remove-Item $tmpEvent, response.json
```

For the `process-batch-transform-results` Lambda invoked with `InProgress`, you should see `"Non-terminal state 'InProgress' - no action taken."` if the terminal-state filter is in effect.

## Troubleshooting

- **`The role defined for the function cannot be assumed by Lambda.`** The role's trust policy does not include `lambda.amazonaws.com`. Update the trust policy to add it (or ask the admin).
- **`ValidationException ... Could not assume role ... for principal sagemaker.amazonaws.com`** when SageMaker tries to use the role you passed in `IAM_ROLE_ARN`. Either the role's trust policy does not include `sagemaker.amazonaws.com`, or your Lambda's role does not have `iam:PassRole` on the SageMaker role. Easiest fix is to use one role that lists both `lambda` and `sagemaker` as trusted principals (then Lambda is "passing itself", which is always allowed).
- **`Cannot create already existing model "..."`** in CloudWatch for `start-batch-transform-job`. The handler should be idempotent. Replace `create_model()` with a `describe_model` check first, then `create_model` only if not found.
- **`AttributeError: 'decimal.Decimal' object has no attribute 'strip'`** in CloudWatch. DynamoDB returns numeric attributes as `Decimal`. Cast `course_id` and `program_id` to `str()` before passing to functions that call `.strip()` or regex on them.
- **EventBridge Lambda flips records to `AWAITING_COMPLETION_FAILED` mid-job.** SageMaker emits state-change events for non-terminal states like `InProgress`. The Lambda must filter for terminal states (`Completed`, `Failed`, `Stopped`) and ignore others.
- **`Expected: '=', received: ''` on `--environment` or `--key`.** PowerShell 5.1 strips inner `"` when passing string args to native executables, and `Out-File -Encoding utf8` adds a UTF-8 BOM that AWS CLI rejects. Always write JSON to a temp file using `[System.IO.File]::WriteAllText($tmpFile, $json, (New-Object System.Text.UTF8Encoding $false))` and pass via `file://$tmpFile`.
- **`Function not found`** when FastAPI tries to invoke the Lambda. The Lambda was not deployed, or the name in `routes.py` does not match the deployed function name (`start-batch-transform-job`).
- **`AccessDeniedException`** at runtime. The Lambda execution role is missing the runtime permission for whichever AWS service it failed on (DynamoDB, S3, SageMaker, etc.). Admin needs to add the missing action.

## Required code prerequisites in the Lambda handlers

Before you deploy, the handler files in `app/lambda_handlers/` must include the following fixes:

- **`lambda_handler_start_batch_tranform_job.py`**
  - In `build_job_name`, cast `course_id` and `program_id` to `str()` before passing them to `_is_known` / `_sanitize_for_job_name` (DynamoDB returns them as `Decimal`).
  - In `create_model`, call `sm.describe_model` first; only create if it does not already exist. Otherwise repeated invocations fail because the model name is fixed.
- **`lambda_handler_process_batch_transform_inference_results.py`**
  - At the top of `lambda_handler`, filter for terminal `TransformJobStatus` values (`Completed`, `Failed`, `Stopped`). Return early on anything else, otherwise the Lambda mishandles `InProgress` events as failures.
